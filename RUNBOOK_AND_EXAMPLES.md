# PILOT-AI Demo: Presentation Runbook & Examples

This guide is designed for your focus group presentation. It covers how to start the system from scratch and provides sample inputs to demonstrate the AI's capabilities to your stakeholders.

---

## 🚀 How to Run the Website

Before your presentation, ensure both the backend and frontend are running.

### 1. Start the Backend Server
Open a terminal (Command Prompt or PowerShell) and run the following commands:
```bash
cd "C:\Users\msi 1\.gemini\antigravity\scratch\pilot-ai-free\backend"
python main.py
```
*Wait until you see `Application startup complete.` in the terminal.*

### 2. Start the Frontend Server
Open a **second** terminal and run:
```bash
cd "C:\Users\msi 1\.gemini\antigravity\scratch\pilot-ai-free\frontend"
npm run dev
```

### 3. Open the App
Open your web browser and go to: **[http://localhost:3000](http://localhost:3000)**

---

## 🧪 Example Prompts for Live Testing

During your focus group, use these examples in the **"Analyse Application"** page to showcase different outcomes.

### Example 1: The "Likely Non-Compliant" Case (Pre-built Demo)
*Use this to show how the AI handles complex constraints and identifies policy conflicts.*

*   **Site Address:** `Former garage site, 14–18 Brayford Street, Lincoln, LN1 3XX`
*   **Application Type:** `Full Planning Permission`
*   **Proposed Development:** `Demolition of existing garages and erection of a 3-storey residential block comprising 12 apartments (8 × 2-bed, 4 × 1-bed) with associated parking (6 spaces) and communal landscaping.`
*   **Site Constraints:** `Conservation Area`, `Flood Zone 2`
*   **Expected Result:** **LikELY NON COMPLIANT**. The AI will flag the lack of a Sequential/Exception Test for Flood Zone 2 and the lack of heritage impact information.

### Example 2: The "Likely Compliant" Case
*Use this to show a straightforward application that aligns well with local design policy.*

*   **Site Address:** `42 High Street, Lincoln, LN2 1AP`
*   **Application Type:** `Householder Application`
*   **Proposed Development:** `Single-storey rear extension using matching red brick and slate roofing to match the host dwelling. The extension projects 3 metres from the original rear wall and maintains existing boundary treatments.`
*   **Site Constraints:** `None known`
*   **Expected Result:** **LIKELY COMPLIANT**. The AI will cite the Lincoln Design SPD regarding matching materials and appropriate scale.

### Example 3: The "Requires Further Info" Case
*Use this to show how the AI reacts when critical details are missing from an application.*

*   **Site Address:** `Plot 4, Industrial Estate, Lincoln, LN6 3QY`
*   **Application Type:** `Full Planning Permission`
*   **Proposed Development:** `Erection of a new commercial warehouse facility for logistics use (Class B8).`
*   **Site Constraints:** `None known`
*   **Expected Result:** **REQUIRES FURTHER INFO**. The AI will note that it lacks details on parking provisions, noise assessments, or hours of operation, which are required by the Local Plan for commercial developments.

---

## 💡 Presentation Tips

*   **Show the Citations:** Always click the `C1 🔍` citation buttons in the Policy Assessment table. This slide-out panel is the "magic moment" where planners see that the AI isn't hallucinating—it's reading their actual PDFs.
*   **Show the System Status:** Go to the Dashboard and point out the `£0.00/month` running cost. Highlight that it is using **Groq** and **local embeddings**, completely removing cloud lock-in.
*   **Upload a PDF Live:** Go to the "Policy Library" tab and upload a short PDF. Show how quickly the document is chunked and indexed into the local vector database, ready to be searched instantly.
