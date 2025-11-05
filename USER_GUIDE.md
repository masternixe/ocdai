# User Guide

Complete guide for using the Document Processing & Liveness Detection System.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Processing Documents](#processing-documents)
3. [Live Capture](#live-capture)
4. [Face Matching](#face-matching)
5. [Viewing History](#viewing-history)
6. [Configuration](#configuration)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching the Application

1. Open terminal/command prompt
2. Navigate to project directory:
   ```bash
   cd /path/to/ocdai
   ```
3. Activate virtual environment (if using):
   ```bash
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
4. Start application:
   ```bash
   streamlit run app.py
   ```
5. Browser opens automatically at: http://localhost:8501

### Interface Overview

The application has 5 main tabs:
- **Upload Document**: Process passports and IDs
- **Live Capture**: Take selfie with liveness check
- **Face Matching**: Compare document vs live face
- **History**: View past processing records
- **Documentation**: In-app help and guides

### Sidebar Settings

- **Processing Mode**: Choose Native or API mode
- **Face Match Threshold**: Adjust matching strictness
- **OCR Confidence**: Set minimum OCR confidence
- **System Info**: View current configuration

---

## Processing Documents

### Step-by-Step

1. **Go to "Upload Document" tab**

2. **Click "Browse files" or drag-and-drop**
   - Supported formats: PDF, JPG, PNG, BMP, TIFF
   - Maximum size: 10MB (default)

3. **Preview uploaded document**
   - Image files show preview
   - PDF files show filename

4. **Click "Process Document"**
   - Processing takes 3-10 seconds
   - Progress indicator shows status

5. **View extracted information**
   - Document type detected automatically
   - All fields displayed in organized format
   - Confidence score shown
   - Extracted face photo displayed

6. **Download results**
   - Click "Download JSON" to save data
   - JSON file contains all extracted fields

### Supported Documents

#### Passports

Extracts:
- Full Name
- Passport Number
- Nationality
- Date of Birth
- Gender
- Issue Date
- Expiry Date
- Place of Birth
- MRZ (Machine Readable Zone)
- Face Photo

**Supported regions**:
- South Asia (India, Pakistan, Bangladesh, Sri Lanka)
- Middle East (UAE, Saudi Arabia, Qatar, Kuwait, etc.)
- Europe (Schengen and non-Schengen)
- Africa
- China
- Russia

#### UAE Emirates ID (EID)

Extracts:
- ID Number (784-XXXX-XXXXXXX-X format)
- Full Name (English and Arabic)
- Nationality
- Date of Birth
- Gender
- Issue Date
- Expiry Date
- Face Photo

#### Other National IDs

Basic extraction for other national identity cards.

### Document Quality Tips

**For best results**:
- Use high-resolution scans (300+ DPI)
- Ensure good lighting (no shadows)
- Keep document flat (no bends/folds)
- Avoid glare and reflections
- Include entire document in frame
- Use color scans (not black & white)

**Avoid**:
- Blurry images
- Low resolution photos
- Partial documents
- Heavy shadows
- Extreme angles

---

## Live Capture

### Taking a Live Selfie

1. **Go to "Live Capture" tab**

2. **Allow camera access**
   - Browser will request permission
   - Click "Allow" to enable camera

3. **Position yourself**
   - Face camera directly
   - Ensure good lighting
   - Remove glasses if possible
   - Keep face centered

4. **Click camera button to capture**
   - Photo is taken instantly
   - Preview shown below

5. **Click "Verify Liveness"**
   - Liveness check runs automatically
   - Takes 1-3 seconds

6. **Review results**
   - Pass/Fail status
   - Liveness score
   - Quality metrics
   - Extracted face shown

### Liveness Detection

The system checks for:

**Active Liveness** (if implemented):
- Blink detection
- Head movement
- Real-time video analysis

**Passive Liveness**:
- Texture analysis
- Color distribution
- Frequency analysis
- JPEG artifact detection

### Quality Checks

System validates:
- **Brightness**: Image not too dark/bright
- **Blur**: Image is sharp and clear
- **Contrast**: Good dynamic range
- **Face Size**: Face is large enough
- **Face Detection**: Face clearly visible

### Liveness Tips

**For best results**:
- Use natural or diffused lighting
- Look directly at camera
- Keep still during capture
- Avoid filters or effects
- Use clean camera lens
- No hats or face coverings

**Avoid**:
- Poor lighting (too dark/bright)
- Motion blur
- Extreme angles
- Photos of photos/screens
- Printed photos
- Video playback

---

## Face Matching

### Comparing Faces

1. **Complete document upload first**
   - Process a document with face photo

2. **Complete live capture second**
   - Take selfie and verify liveness

3. **Go to "Face Matching" tab**

4. **Review side-by-side preview**
   - Document face (left)
   - Live face (right)

5. **Click "Compare Faces"**
   - Matching algorithm runs
   - Takes 1-3 seconds

6. **Review match results**
   - Pass/Fail decision
   - Match score (0-100%)
   - Confidence level
   - Threshold used

### Understanding Match Scores

**Match Score**: Similarity between faces (0.0 - 1.0)
- 0.9 - 1.0: Excellent match
- 0.7 - 0.9: Good match
- 0.6 - 0.7: Fair match (default threshold)
- 0.4 - 0.6: Poor match
- 0.0 - 0.4: No match

**Threshold**: Minimum score required for "Pass"
- Default: 0.6 (60%)
- Adjustable in sidebar
- Lower = more strict
- Higher = more lenient

### Match Result Interpretation

✅ **MATCH (Pass)**:
- Score exceeds threshold
- High confidence faces are same person
- Proceed with verification

❌ **NO MATCH (Fail)**:
- Score below threshold
- Faces likely different people
- Require re-verification

### Factors Affecting Matching

**Positive factors**:
- Similar lighting conditions
- Similar face angles
- Clear, high-quality images
- Recent photos (age similarity)
- Consistent facial hair/accessories

**Negative factors**:
- Different lighting/shadows
- Different angles/expressions
- Poor image quality
- Significant age difference
- Major appearance changes

---

## Viewing History

### Accessing Records

1. **Go to "History" tab**

2. **View recent records table**
   - Shows last 50 records
   - Columns: ID, Type, File, Confidence, Date, Status

3. **Enter ID to view details**
   - Type record ID in input box
   - Click "View Details"

4. **Review full record**
   - All extracted data shown
   - JSON format for easy reading

### Record Information

Each record contains:
- Document ID (unique)
- Document type
- Original filename
- Processing mode used
- Extracted data (all fields)
- Confidence score
- Processing timestamp
- Status (completed/failed)

---

## Configuration

### Processing Mode

**Native Mode** (Default):
- Uses open-source libraries
- Free to use
- Works offline
- Good accuracy
- Recommended for most use cases

**API Mode** (Optional):
- Uses cloud services (Azure/AWS/Google)
- Higher accuracy
- Requires API keys and internet
- May incur costs
- Better for production use

**Switching modes**:
- Select in sidebar radio button
- Changes apply immediately
- Previous records unaffected

### Threshold Settings

**Face Match Threshold** (0.0 - 1.0):
- Default: 0.6
- Lower = stricter matching
- Higher = more lenient
- Adjust based on use case:
  - High security: 0.5 - 0.6
  - Normal use: 0.6 - 0.7
  - Lenient: 0.7 - 0.8

**OCR Confidence** (0 - 100):
- Default: 60%
- Minimum confidence for text extraction
- Lower = more words accepted
- Higher = only high-confidence words
- Adjust if getting too much/little text

---

## Tips & Best Practices

### Document Processing

1. **Use high-quality scans** - Higher DPI = better results
2. **Good lighting** - Avoid shadows and glare
3. **Straight orientation** - Rotate images if needed
4. **Complete document** - Include all edges
5. **Try API mode** - If native mode accuracy is low

### Live Capture

1. **Natural lighting** - Face bright but not washed out
2. **Look at camera** - Direct eye contact
3. **Keep still** - Avoid motion blur
4. **Clean lens** - Wipe camera before capture
5. **Try multiple times** - If liveness fails

### Face Matching

1. **Similar conditions** - Match lighting/angle to document
2. **Clear images** - Both faces should be sharp
3. **Adjust threshold** - If getting false results
4. **Check quality** - Review individual quality scores
5. **Re-capture if needed** - Poor quality = poor matching

### General

1. **Check confidence scores** - Low scores may indicate issues
2. **Review extracted data** - Verify accuracy
3. **Save important results** - Download JSON files
4. **Use correct document type** - System auto-detects but verify
5. **Read error messages** - They explain what went wrong

---

## Troubleshooting

### Document Processing Issues

**Problem**: "Could not load document"
- **Solution**: Check file format (PDF, JPG, PNG only)
- **Solution**: Verify file is not corrupted
- **Solution**: Try different file

**Problem**: Low confidence score (< 50%)
- **Solution**: Use higher resolution image
- **Solution**: Improve lighting/scanning quality
- **Solution**: Try API mode
- **Solution**: Manually verify extracted data

**Problem**: No face detected
- **Solution**: Ensure face photo is visible
- **Solution**: Try higher resolution scan
- **Solution**: Check document orientation
- **Solution**: Crop to include face clearly

**Problem**: Wrong document type detected
- **Solution**: System does best guess based on content
- **Solution**: Extracted data still saved
- **Solution**: Note correct type manually

### Live Capture Issues

**Problem**: Camera not working
- **Solution**: Check browser permissions
- **Solution**: Ensure camera is connected
- **Solution**: Close other apps using camera
- **Solution**: Try different browser
- **Solution**: Use HTTPS or localhost

**Problem**: Liveness check fails
- **Solution**: Improve lighting
- **Solution**: Look directly at camera
- **Solution**: Remove glasses
- **Solution**: Keep still during capture
- **Solution**: Avoid using photos/screens

**Problem**: Poor quality warnings
- **Solution**: Add more light
- **Solution**: Clean camera lens
- **Solution**: Check camera resolution settings
- **Solution**: Move closer to light source

### Face Matching Issues

**Problem**: False negatives (same person, no match)
- **Solution**: Lower match threshold
- **Solution**: Improve image quality
- **Solution**: Ensure similar lighting
- **Solution**: Take new photos

**Problem**: False positives (different people, match)
- **Solution**: Raise match threshold
- **Solution**: Verify liveness passed
- **Solution**: Check quality scores
- **Solution**: Re-capture both images

**Problem**: "No face detected" error
- **Solution**: Ensure both faces were extracted
- **Solution**: Go back and re-process document
- **Solution**: Re-capture live selfie
- **Solution**: Check image quality

### Application Issues

**Problem**: Application won't start
- **Solution**: Check Python installed correctly
- **Solution**: Install dependencies: `pip install -r requirements.txt`
- **Solution**: Check for error messages in terminal

**Problem**: Slow performance
- **Solution**: Close other applications
- **Solution**: Reduce image file sizes
- **Solution**: Check system resources
- **Solution**: Update configuration for fewer workers

**Problem**: Database errors
- **Solution**: Delete `documents.db` to reset
- **Solution**: Run: `python -c "from models import init_db; init_db()"`

---

## Keyboard Shortcuts

- `Ctrl/Cmd + R`: Refresh page
- `Ctrl/Cmd + K`: Clear cache
- `Ctrl/Cmd + Shift + R`: Hard refresh

---

## Getting Help

### In-App Help

- Go to "Documentation" tab
- Read tooltips (hover over ℹ️ icons)
- Check sidebar for system info

### External Resources

- README.md: Project overview
- INSTALL.md: Installation guide
- API.md: API documentation

### Support

For technical support:
1. Check error messages carefully
2. Review this user guide
3. Try troubleshooting steps
4. Check system logs
5. Contact technical support team

---

## Updates

Check for updates periodically:
```bash
git pull
pip install -r requirements.txt --upgrade
```

Restart application after updates.

---

## Best Use Cases

### Identity Verification
- Onboarding new customers
- KYC (Know Your Customer) compliance
- Age verification
- Identity authentication

### Border Control
- Passport verification
- Visa processing
- Entry/exit validation

### Financial Services
- Account opening
- Loan applications
- Transaction verification

### Healthcare
- Patient registration
- Insurance verification
- Prescription validation

### Government Services
- Citizen services
- License issuance
- Benefit applications

---

## Data Privacy

- Documents stored locally
- No data sent to cloud (native mode)
- Delete records from History tab
- Secure API key storage
- HTTPS in production

---

## Accessibility

- Keyboard navigation supported
- Screen reader compatible
- High contrast mode available
- Adjustable text sizes
- Alternative input methods

---

**Version**: 1.0.0  
**Last Updated**: 2024

For the latest version of this guide, check the application's Documentation tab.

