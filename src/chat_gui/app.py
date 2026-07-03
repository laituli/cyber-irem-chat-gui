"""Gradio GUI for cyber-irem chat."""
import gradio as gr
from typing import Optional
from chat_gui.backend import ChatBackend


def create_app(backend: str = "mock", model: Optional[str] = None) -> gr.Blocks:
    """Create the Gradio app."""
    chat_backend = ChatBackend(backend=backend, model=model)

    def transform_fn(text: str, n_variants: int):
        """Transform text and return list of messages as HTML."""
        import asyncio
        import base64
        from pathlib import Path
        
        if not text.strip():
            return "<p>请输入文本</p>"

        messages = asyncio.run(chat_backend.transform(text, int(n_variants)))

        html = ['<div style="display:flex;flex-direction:column;gap:12px;">']
        for msg in messages:
            emote_html = ""
            if msg.emote and Path(msg.emote).exists():
                data = Path(msg.emote).read_bytes()
                suffix = Path(msg.emote).suffix.lower().lstrip(".")
                mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(suffix, "png")
                b64 = base64.b64encode(data).decode()
                emote_html = f'<img src="data:image/{mime};base64,{b64}" style="width:64px;height:64px;border-radius:8px;object-fit:cover;" />'

            html.append(f'''<div style="display:flex;align-items:flex-start;gap:10px;background:#f8f0ff;border-radius:12px;padding:10px 14px;">
  {emote_html}
  <span style="line-height:1.6;font-size:15px;">{msg.display()}</span>
</div>''')
        html.append('</div>')
        return "\n".join(html)

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
                output = gr.HTML(label="转换结果", value="<p>等待转换...</p>")

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
