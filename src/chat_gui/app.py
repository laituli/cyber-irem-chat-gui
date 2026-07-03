"""Gradio GUI for cyber-irem chat."""
import gradio as gr
from typing import Optional
from chat_gui.backend import ChatBackend


def create_app(backend: str = "mock", model: Optional[str] = None) -> gr.Blocks:
    """Create the Gradio app."""
    chat_backend = ChatBackend(backend=backend, model=model)

    def transform_fn(text: str, n_variants: int):
        """Transform text and return list of messages."""
        import asyncio
        
        if not text.strip():
            return "请输入文本"

        messages = asyncio.run(chat_backend.transform(text, int(n_variants)))

        # Format output
        output = []
        for i, msg in enumerate(messages, 1):
            output.append(f"### 消息 {i}")
            output.append(f"- **文本**: {msg.text}")
            output.append(f"- **心情**: {msg.mood}")
            if msg.kaomoji:
                output.append(f"- **颜文字**: {msg.kaomoji}")
            if msg.action:
                output.append(f"- **动作**: {msg.action}")
            if msg.suffix:
                output.append(f"- **后缀**: {msg.suffix}")
            output.append(f"- **完整显示**: {msg.display()}")
            output.append("")

        return "\n".join(output)

    with gr.Blocks(title="Cyber Irem - 猫娘聊天工具") as app:
        gr.Markdown("# 🐱 Cyber Irem - 猫娘聊天工具")
        gr.Markdown("将文本转换为可爱的猫娘风格")

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="输入文本",
                    placeholder="输入要转换的文本...",
                    lines=3
                )
                n_variants = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=3,
                    step=1,
                    label="生成变体数量"
                )
                transform_btn = gr.Button("转换", variant="primary")

            with gr.Column():
                output = gr.Markdown(label="转换结果", value="等待转换...")

        transform_btn.click(
            fn=transform_fn,
            inputs=[input_text, n_variants],
            outputs=output
        )

    return app


def main():
    """Run the Gradio app."""
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="mock", choices=["mock", "ollama", "openai"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    app = create_app(backend=args.backend, model=args.model)
    print(f"\n🐱 Starting cyber-irem chat GUI...")
    print(f"📡 Backend: {args.backend}")
    print(f"🌐 Open in browser: http://localhost:{args.port}\n", flush=True)
    sys.stdout.flush()
    app.launch(server_port=args.port, inbrowser=False, share=False)


if __name__ == "__main__":
    main()
