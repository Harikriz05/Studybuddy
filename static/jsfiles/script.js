const fileInput = document.getElementById("file-input");
const uploadButton = document.getElementById("upload-button");
const noteList = document.getElementById("note-list");

uploadButton.addEventListener("click", () => {
    const file = fileInput.files[0];
    if (file) {
        const fileURL = URL.createObjectURL(file);
        const noteItem = createNoteItem(fileURL, file.name);
        noteList.appendChild(noteItem);
        fileInput.value = null; // Clear the input
    }
});

function createNoteItem(fileURL, fileName) {
    const noteItem = document.createElement("li");
    noteItem.className = "note-item";
    
    const link = document.createElement("a");
    link.href = fileURL;
    link.target = "_blank";
    link.textContent = fileName;
    
    const deleteButton = document.createElement("span");
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => {
        noteList.removeChild(noteItem);
    });

    noteItem.appendChild(link);
    noteItem.appendChild(deleteButton);
    
    return noteItem;
}
