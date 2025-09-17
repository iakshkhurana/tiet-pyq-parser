# TIET PYQ Parser 🎓

A comprehensive web application for downloading previous year question papers from Thapar Institute of Engineering and Technology (TIET). This tool automates the process of searching and downloading question papers, making it easier for students to access study materials.

## 🚀 Features

- **Smart Search**: Search by course code or course name
- **Automated Download**: Automatically downloads PDFs from the TIET website
- **PDF Merging**: Option to merge multiple PDFs into a single file
- **Exam Type Filtering**: Filter papers by exam type (MST, EST, AUX)
- **Modern Web Interface**: Clean, responsive UI built with Next.js
- **Course Code Normalization**: Handles various course code formats automatically
- **Batch Processing**: Download multiple papers at once

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Chrome browser (for Selenium automation)

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🚀 Running the Application

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## 📖 Usage

1. **Open the Web Interface**: Navigate to `http://localhost:3000`
2. **Choose Search Type**: Select either "Course Code" or "Course Name"
3. **Enter Search Query**: 
   - For course code: Enter codes like `UCS301`, `ucs-301`, or `UCS 301`
   - For course name: Enter partial course names like "Data Structures"
4. **Configure Options**:
   - Select exam type filter (All Types, MST Only, EST Only, AUX Only)
   - Choose whether to merge PDFs into a single file
5. **Submit**: Click the submit button to start the download process

### Command Line Usage

You can also run the parser directly from the command line:

```bash
cd exam-parser
python tiet_papers_downloader.py [option] [value] [mergePdfs] [examFilter]
```

Parameters:
- `option`: 1 for course code, 2 for course name
- `value`: The search term
- `mergePdfs`: true/false to merge PDFs
- `examFilter`: "all", "MST", "EST", or "AUX"

Example:
```bash
python tiet_papers_downloader.py 1 UCS301 true MST
```

## 📁 Project Structure

```
tiet-pyq-parser/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main API endpoints
│   └── requirements.txt    # Python dependencies
├── exam-parser/            # Core parsing logic
│   ├── tiet_papers_downloader.py  # Main parser script
│   └── downloads/          # Downloaded files directory
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── package.json       # Node.js dependencies
├── others/                # Additional resources
│   └── demo.mp4          # Demo video
└── README.md             # This file
```

## 🎥 Demo

Watch the demo video to see the application in action:

[![Demo Video](https://img.shields.io/badge/📹%20Watch%20Demo-Demo%20Video-red?style=for-the-badge)](https://github.com/iakshkhurana/tiet-pyq-parser/blob/main/others/demo.mp4)

## 🔧 Technical Details

### Backend (FastAPI)
- **Framework**: FastAPI for high-performance API
- **CORS**: Configured for cross-origin requests
- **Subprocess**: Executes Python scripts with proper error handling

### Frontend (Next.js)
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS for modern UI
- **Components**: Custom loading buttons and animations
- **State Management**: React hooks for form state

### Parser (Selenium)
- **Browser Automation**: Chrome WebDriver with headless mode
- **Smart Waiting**: Robust waiting strategies for dynamic content
- **Error Handling**: Comprehensive error handling and retry logic
- **PDF Processing**: PyPDF2 for merging multiple PDFs

## 📝 API Endpoints

### POST `/run-script`
Executes the paper download script with the provided parameters.

**Request Body:**
```json
{
  "option": "1",
  "value": "UCS301",
  "mergePdfs": true,
  "examFilter": "MST"
}
```

**Response:**
```json
{
  "output": "SUCCESS: Downloaded 5/5 file(s) to Downloads/ThaparPapers/",
  "error": ""
}
```

### GET `/`
Health check endpoint that returns the server status.

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: Ensure Chrome browser is installed and up to date
2. **Permission Errors**: Make sure the script has write permissions to the Downloads folder
3. **Network Timeouts**: Check your internet connection and try again
4. **No Results Found**: Verify the course code/name is correct and exists in the database

### Debug Mode

To run the parser in debug mode (with visible browser):
```python
# In tiet_papers_downloader.py, change:
HEADLESS = False
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thapar Institute of Engineering and Technology for providing the question paper database
- The open-source community for the amazing tools and libraries used in this project

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/iakshkhurana/tiet-pyq-parser/issues) page
2. Create a new issue with detailed information
3. Contact the maintainer

---

**Note**: This tool is for educational purposes only. Please respect the institute's terms of service and use responsibly.
