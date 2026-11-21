from pptx import Presentation

pptx_path = r'C:\Users\madha\.gemini\antigravity\brain\c8e072c0-e062-4c2a-8b6c-36873f818d11\.user_uploaded\media_1795017468940_8b29693e.pptx'
prs = Presentation(pptx_path)

print("Total Slides:", len(prs.slides))
print("Slide Size: %.2f w x %.2f h inches" % (prs.slide_width.inches, prs.slide_height.inches))
print()

for i, slide in enumerate(prs.slides):
    layout_name = slide.slide_layout.name if slide.slide_layout else 'Unknown'
    print("=== SLIDE %d (Layout: %s) ===" % (i+1, layout_name))
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    font_info = ''
                    if para.runs:
                        r = para.runs[0]
                        sz = r.font.size
                        bold = r.font.bold
                        try:
                            color = str(r.font.color.rgb) if r.font.color and r.font.color.type else 'inherit'
                        except:
                            color = 'inherit'
                        sz_pt = int(sz.pt) if sz else '?'
                        font_info = " [sz=%spt bold=%s color=%s]" % (sz_pt, bold, color)
                    print("  %s%s" % (text[:100], font_info))
    print()

