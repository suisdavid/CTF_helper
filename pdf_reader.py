import PyPDF2
with open('chall.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f"Number of pages: {len(reader.pages)}")
    print(f"Metadata: {reader.metadata}")
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"\n=== Page {i+1} text ===")
        print(repr(text))
        print(f"=== Page {i+1} visible ===")
        print(text)
