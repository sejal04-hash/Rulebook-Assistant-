
const API_BASE = "";

let selectedDocumentId = null;
let selectedDocumentName = null;

// ==========================================
// 1. DOM ELEMENTS
// ==========================================

const uploadForm = document.getElementById("uploadForm");
const pdfInput = document.getElementById("pdfInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const selectedFileName = document.getElementById("selectedFileName");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const documentsList = document.getElementById("documentsList");
const allDocumentsList = document.getElementById("allDocumentsList");
const sidebarDocuments = document.getElementById("sidebarDocuments");

const documentCount = document.getElementById("documentCount");
const pageCount = document.getElementById("pageCount");
const chunkCount = document.getElementById("chunkCount");

const questionForm = document.getElementById("questionForm");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");

const selectedDocumentNameElement =
    document.getElementById("selectedDocumentName");

const selectedDocumentStatus =
    document.getElementById("selectedDocumentStatus");


// ==========================================
// 2. NAVIGATION
// ==========================================

function showView(viewId) {
    document.querySelectorAll(".page-view").forEach(view => {
        view.classList.add("hidden");
    });

    const selectedView = document.getElementById(viewId);

    if (selectedView) {
        selectedView.classList.remove("hidden");
    }

    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.remove("active");
    });
}

document.getElementById("chatNav")?.addEventListener("click", () => {
    showView("chatView");
    document.getElementById("chatNav").classList.add("active");
});

document.getElementById("documentsNav")?.addEventListener("click", () => {
    showView("documentsView");
    document.getElementById("documentsNav").classList.add("active");
    loadDocuments();
});

document.getElementById("historyNav")?.addEventListener("click", () => {
    showView("historyView");
    document.getElementById("historyNav").classList.add("active");
});

document.getElementById("refreshDocumentsBtn")?.addEventListener(
    "click",
    loadDocuments
);

document.getElementById("viewAllDocumentsBtn")?.addEventListener(
    "click",
    () => {
        showView("documentsView");
        loadDocuments();
    }
);


// ==========================================
// 3. PDF FILE SELECTION
// ==========================================

browseBtn?.addEventListener("click", event => {
    event.stopPropagation();
    pdfInput.click();
});

dropZone?.addEventListener("click", event => {
    if (!event.target.closest("#browseBtn")) {
        pdfInput.click();
    }
});

pdfInput?.addEventListener("change", () => {
    handleFileSelection(pdfInput.files[0]);
});

function handleFileSelection(file) {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        uploadStatus.textContent = "Please select a PDF file.";
        uploadStatus.className = "status-message error";
        pdfInput.value = "";
        return;
    }

    selectedFileName.textContent = file.name;
    uploadStatus.textContent = "";
    uploadStatus.className = "status-message";
}


// ==========================================
// 4. DRAG AND DROP
// ==========================================

dropZone?.addEventListener("dragover", event => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone?.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone?.addEventListener("drop", event => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        uploadStatus.textContent = "Please drop a PDF file.";
        uploadStatus.className = "status-message error";
        return;
    }

    pdfInput.files = event.dataTransfer.files;
    handleFileSelection(file);
});


// ==========================================
// 5. UPLOAD PDF
// ==========================================

uploadForm?.addEventListener("submit", async event => {
    event.preventDefault();

    const file = pdfInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a PDF first.";
        uploadStatus.className = "status-message error";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Processing PDF...";
    uploadStatus.textContent =
        "Uploading and processing your PDF. Please wait...";

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Upload failed.");
        }

        uploadStatus.textContent =
            `Successfully uploaded ${result.filename}! ` +
            `${result.total_pages} pages and ` +
            `${result.total_chunks} chunks created.`;

        uploadStatus.className = "status-message success";

        selectDocument(result.document_id, result.filename);

        uploadForm.reset();
        selectedFileName.textContent = "No file selected";

        await loadDocuments();

    } catch (error) {
        uploadStatus.textContent = error.message;
        uploadStatus.className = "status-message error";

    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload Document";
    }
});


// ==========================================
// 6. LOAD DOCUMENTS FROM FASTAPI
// ==========================================

async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`);

        if (!response.ok) {
            throw new Error("Could not load documents.");
        }

        const data = await response.json();
        const documents = data.documents || [];

        renderDocuments(documents);
        updateStatistics(documents);

    } catch (error) {
        console.error("Document loading error:", error);
    }
}


// ==========================================
// 7. GET ACTUAL PDF FILENAME
// ==========================================

function getDocumentFilename(doc) {
    return (
        doc.filename ||
        doc.source ||
        doc.file_name ||
        doc.name ||
        doc.original_filename ||
        "Untitled PDF"
    );
}


// ==========================================
// 8. RENDER DOCUMENTS
// ==========================================

function renderDocuments(documents) {
    documentsList.replaceChildren();
    allDocumentsList.replaceChildren();
    sidebarDocuments.replaceChildren();

    if (documents.length === 0) {
        documentsList.innerHTML = `
            <div class="empty-state">
                <div>📄</div>
                <h3>No PDFs uploaded yet</h3>
                <p>Upload a PDF above to start asking questions.</p>
            </div>
        `;

        allDocumentsList.innerHTML = `
            <div class="empty-state">
                <div>📚</div>
                <h3>Your library is empty</h3>
                <p>Upload your first PDF to see it here.</p>
            </div>
        `;

        sidebarDocuments.innerHTML = `
            <p class="empty-sidebar">
                Your uploaded PDFs will appear here.
            </p>
        `;

        return;
    }

    documents.forEach(doc => {
        documentsList.appendChild(createDocumentCard(doc));
        allDocumentsList.appendChild(createDocumentCard(doc));
        sidebarDocuments.appendChild(createSidebarDocument(doc));
    });
}


// ==========================================
// 9. CREATE DOCUMENT CARD
// ==========================================

function createDocumentCard(doc) {
    const card = document.createElement("article");
    card.className = "document-card";

    const icon = document.createElement("div");
    icon.className = "document-icon";
    icon.textContent = "PDF";

    const filename = getDocumentFilename(doc);

    const title = document.createElement("h3");
    title.textContent = filename;
    title.title = filename;

    const details = document.createElement("p");

    const totalChunks = doc.total_chunks ?? doc.chunk_count ?? 0;

    details.textContent =
        `${doc.total_pages || 0} pages · ${totalChunks} text chunks`;

    const actions = document.createElement("div");
    actions.className = "document-actions";

    // Chat button
    const chatButton = document.createElement("button");
    chatButton.type = "button";
    chatButton.className = "open-chat-btn";
    chatButton.textContent = "Chat with PDF";

    chatButton.addEventListener("click", () => {
        selectDocument(doc.document_id, filename);
        showView("chatView");
        document.getElementById("chatNav")?.classList.add("active");
    });

    // Delete button
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-btn";
    deleteButton.textContent = "Delete";

    deleteButton.addEventListener("click", () => {
        deleteDocument(doc.document_id, filename);
    });

    actions.append(chatButton, deleteButton);
    card.append(icon, title, details, actions);

    return card;
}


// ==========================================
// 10. SIDEBAR DOCUMENTS
// ==========================================

function createSidebarDocument(doc) {
    const item = document.createElement("button");

    item.type = "button";
    item.className = "sidebar-document";

    const filename = getDocumentFilename(doc);

    item.textContent = filename;
    item.title = filename;

    item.addEventListener("click", () => {
        selectDocument(doc.document_id, filename);
        showView("chatView");
        document.getElementById("chatNav")?.classList.add("active");
    });

    return item;
}


// ==========================================
// 11. DASHBOARD STATISTICS
// ==========================================

function updateStatistics(documents) {
    documentCount.textContent = documents.length;

    const totalPages = documents.reduce(
        (sum, doc) => sum + (Number(doc.total_pages) || 0),
        0
    );

    const totalChunks = documents.reduce(
        (sum, doc) => sum + (
            Number(doc.total_chunks ?? doc.chunk_count) || 0
        ),
        0
    );

    pageCount.textContent = totalPages;
    chunkCount.textContent = totalChunks;
}


// ==========================================
// 12. SELECT PDF
// ==========================================

function selectDocument(documentId, filename) {
    selectedDocumentId = documentId;
    selectedDocumentName = filename || "Selected PDF";

    selectedDocumentNameElement.textContent = selectedDocumentName;
    selectedDocumentStatus.textContent = "Ready to chat";

    chatMessages.replaceChildren();

    addMessage(
        "assistant",
        `You're chatting with "${selectedDocumentName}".\n\n` +
        "Ask a question below, or try one of the suggested questions."
    );
}


// ==========================================
// 13. DELETE PDF
// ==========================================

async function deleteDocument(documentId, filename) {
    const confirmed = confirm(
        `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) return;

    try {
        const response = await fetch(
            `${API_BASE}/documents/${encodeURIComponent(documentId)}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Could not delete document."
            );
        }

        if (selectedDocumentId === documentId) {
            selectedDocumentId = null;
            selectedDocumentName = null;

            selectedDocumentNameElement.textContent =
                "No document selected";

            selectedDocumentStatus.textContent =
                "Select a PDF to start";

            chatMessages.replaceChildren();
        }

        await loadDocuments();

        alert("Document deleted successfully.");

    } catch (error) {
        alert(error.message);
    }
}


// ==========================================
// 14. DISPLAY CHAT MESSAGE
// ==========================================

function addMessage(role, text, pages = []) {
    const message = document.createElement("div");
    message.className = `message ${role}`;

    const content = document.createElement("div");
    content.className = "message-content";

    // textContent prevents PDF/LLM text from being interpreted as HTML.
    content.textContent = text;
    content.style.whiteSpace = "pre-wrap";

    message.appendChild(content);

    if (pages.length > 0) {
        const meta = document.createElement("div");
        meta.className = "message-meta";

        meta.textContent =
            `Sources: ${pages.map(page => `Page ${page}`).join(", ")}`;

        message.appendChild(meta);
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ==========================================
// 15. ASK QUESTION
// ==========================================

questionForm?.addEventListener("submit", async event => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) return;

    if (!selectedDocumentId) {
        alert("Please select or upload a PDF first.");
        return;
    }

    addMessage("user", question);

    questionInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Thinking…";

    try {
        const response = await fetch(`${API_BASE}/ask`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question,
                document_id: selectedDocumentId
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Something went wrong."
            );
        }

        addMessage(
            "assistant",
            result.answer,
            result.source_pages || []
        );

    } catch (error) {
        addMessage(
            "assistant",
            `Sorry, I could not complete that request.\n${error.message}`
        );

    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send";
        questionInput.focus();
    }
});


// ==========================================
// 16. SUGGESTED QUESTIONS
// ==========================================

document.querySelectorAll(".suggestion-btn").forEach(button => {
    button.addEventListener("click", () => {
        questionInput.value = button.textContent.trim();
        questionInput.focus();
    });
});


// ==========================================
// 17. NEW CHAT
// ==========================================

document.getElementById("newChatBtn")?.addEventListener("click", () => {
    chatMessages.replaceChildren();

    if (selectedDocumentId) {
        addMessage(
            "assistant",
            `New conversation started with "${selectedDocumentName}".\n\n` +
            "What would you like to know?"
        );
    } else {
        addMessage(
            "assistant",
            "Please upload or select a PDF to get started."
        );
    }
});


// ==========================================
// 18. KEYBOARD SHORTCUT
// ==========================================

// Enter = Send question
// Shift + Enter = New line

questionInput?.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        questionForm.requestSubmit();
    }
});


// ==========================================
// 19. INITIAL APPLICATION LOAD
// ==========================================

loadDocuments();
