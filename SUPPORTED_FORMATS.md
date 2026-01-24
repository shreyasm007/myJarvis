# Supported Document Formats

Your RAG chatbot now supports **15 different file formats**!

## 📝 Text Formats
- `.txt` - Plain text files
- `.md` - Markdown files  
- `.markdown` - Markdown files

## 📄 Document Formats
- `.pdf` - PDF documents (resumes, papers, reports)
- `.docx` - Microsoft Word documents
- `.doc` - Legacy Word documents
- `.odt` - OpenOffice/LibreOffice documents
- `.rtf` - Rich Text Format

## 🌐 Web Formats
- `.html` - HTML web pages
- `.htm` - HTML web pages

## 📊 Data Formats
- `.csv` - Comma-separated values (tables, lists)
- `.json` - JSON structured data
- `.xml` - XML structured data

## 📊 Presentation Formats
- `.ppt` - PowerPoint presentations (legacy)
- `.pptx` - PowerPoint presentations (modern)

---

## How to Use

1. **Add your files** to `backend/data/documents/`
2. **Run ingestion**: `python -m scripts.ingest`
3. **Done!** All formats are automatically detected and processed

## Examples

### Portfolio Use Cases
```
backend/data/documents/
├── resume.pdf                 # Your resume
├── projects.md                # Project descriptions
├── skills.csv                 # Skills matrix
├── bio.docx                   # Biography
├── achievements.json          # Structured achievements
├── presentation.pptx          # Project presentation
└── blog-posts.html           # Exported blog content
```

### How Each Format is Processed

- **PDF**: Extracts text from all pages
- **DOCX/ODT/RTF**: Extracts paragraphs and text
- **HTML**: Removes scripts/styles, extracts clean text
- **CSV**: Converts rows to "Column: Value" format
- **JSON**: Converts to readable key-value text
- **XML**: Converts to hierarchical text representation
- **PowerPoint**: Extracts text from all slides

---

## Tips

### Best Practices
✅ Use **descriptive filenames** (e.g., `software-projects.md` not `doc1.md`)  
✅ **Mix formats** - Use what's easiest for each content type  
✅ Keep **one topic per file** for better retrieval  
✅ Use **markdown** for written content (best for LLMs)

### File Size
- Small files (< 1MB) work best
- Large PDFs will be chunked automatically
- Very large files (> 10MB) should be split

### Organization
```
documents/
├── about/
│   ├── bio.md
│   └── resume.pdf
├── projects/
│   ├── project1.md
│   ├── project2.pdf
│   └── demos.pptx
└── skills/
    ├── technical.csv
    └── certifications.json
```

Subdirectories are supported! The folder structure will be reflected in metadata.

---

## Troubleshooting

### "Failed to read document"
- Check file isn't corrupted
- Ensure it's a valid format
- Try opening it in its native application first

### "No text extracted"
- **PDF**: Might be image-based (needs OCR, not supported yet)
- **DOCX**: Might be template-only with no content
- **HTML**: Might be JavaScript-heavy (only static content extracted)

### Low-Quality Extraction
- **PDFs with images**: Text-only PDFs work best
- **Complex tables**: CSV works better than PDF tables
- **Formatted content**: Markdown > DOCX for LLM understanding

---

## Coming Soon (Not Yet Supported)

- 📸 **Image OCR** - Extract text from images in PDFs
- 🎤 **Audio transcription** - Convert audio to text
- 🎬 **Video subtitles** - Extract from video files
- 📧 **Email files** (.eml, .msg)
- 📐 **Spreadsheets** (.xlsx with multiple sheets)

---

**Ready to use!** Just drop any supported file in `backend/data/documents/` and run ingestion. 🚀
