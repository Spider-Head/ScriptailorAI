let editorInstance;

// Function to initialize CKEditor
function initializeEditor(content) {
    ClassicEditor.create(document.querySelector('#editor'))
        .then(editor => {
            editorInstance = editor;
            editorInstance.setData(content);
        })
        .catch(error => {
            console.error(error);
        });
}

// Function to add edit and regenerate buttons to each paragraph
function addEditButtonsToParagraphs() {
    const articleContainer = document.getElementById('articleContainer');
    const paragraphs = articleContainer.querySelectorAll('p');

    paragraphs.forEach((paragraph, index) => {
        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        editButton.addEventListener('click', () => editParagraph(paragraph, index));

        const regenerateButton = document.createElement('button');
        regenerateButton.textContent = 'Regenerate';
        regenerateButton.addEventListener('click', () => regenerateParagraph(index));

        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';
        buttonContainer.appendChild(editButton);
        buttonContainer.appendChild(regenerateButton);

        paragraph.insertAdjacentElement('afterend', buttonContainer);
    });
}

document.getElementById('generateForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const topic = document.getElementById('topic').value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topic: topic })
    })
    .then(response => response.json())
    .then(data => {
        const articleContainer = document.getElementById('articleContainer');
        articleContainer.innerHTML = data.response;

        // Add edit and regenerate buttons to each paragraph
        addEditButtonsToParagraphs();

        // Show additional UI elements
        document.getElementById('editButton').style.display = 'block';
        document.getElementById('uploadImageForm').style.display = 'block';
        document.getElementById('downloadButton').style.display = 'block';
        document.getElementById('saveEditsButton').style.display = 'block';
        document.getElementById('templateOptions').style.display = 'block';

        // Change generate button text and functionality
        const generateButton = document.getElementById('generateButton');
        generateButton.textContent = 'Re-generate';
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle errors gracefully, e.g., show an error message to the user
    });
});

document.getElementById('editButton').addEventListener('click', function() {
    const articleContent = document.getElementById('articleContainer').innerHTML;
    document.getElementById('templateOptions').style.display = 'none';
    document.getElementById('generateForm').style.display = 'none';
    document.getElementById('articleContainer').style.display = 'none'; // Hide the generated content container
    document.getElementById('editorContainer').style.display = 'block'; // Show the text editor container
    initializeEditor(articleContent);
});

document.getElementById('applyTemplateButton').addEventListener('click', function() {
    const selectedTemplate = document.querySelector('input[name="template"]:checked').value;
    const content = editorInstance.getData();

    fetch('/apply_template', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: content, template: selectedTemplate })
    })
    .then(response => response.json())
    .then(data => {
        editorInstance.setData(data.formatted_content);
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle errors gracefully, e.g., show an error message to the user
    });
});

document.getElementById('uploadImageForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('imageUpload');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (editorInstance && document.getElementById('editorContainer').style.display === 'block') {
                editorInstance.model.change(writer => {
                    const insertPosition = editorInstance.model.document.selection.getFirstPosition();
                    writer.insertElement('imageBlock', { src: e.target.result }, insertPosition);
                });
            } else {
                const articleContainer = document.getElementById('articleContainer');
                const imgElement = document.createElement('img');
                imgElement.src = e.target.result;
                imgElement.alt = "Uploaded Image";
                imgElement.style.maxWidth = '100%';
                articleContainer.insertAdjacentElement('afterbegin', imgElement);
            }
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('downloadButton').addEventListener('click', function() {
    const content = editorInstance.getData();
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'article.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

document.getElementById('saveEditsButton').addEventListener('click', function() {
    const content = editorInstance.getData();

    fetch('/save_edits', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ articles: [{ content: content }] })
    })
    .then(response => {
        if (response.ok) {
            alert('Edits saved successfully!');
        } else {
            alert('Failed to save edits.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving edits.');
    });
});

function editParagraph(paragraph, index) {
    const textarea = document.createElement('textarea');
    textarea.value = paragraph.textContent;

    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.addEventListener('click', () => {
        paragraph.textContent = textarea.value;
        textarea.remove();
        saveButton.remove();
    });

    paragraph.insertAdjacentElement('afterend', textarea);
    textarea.insertAdjacentElement('afterend', saveButton);
}

function regenerateParagraph(index) {
    fetch(`/regenerate_paragraph/${index}`)
    .then(response => response.json())
    .then(data => {
        const articleContainer = document.getElementById('articleContainer');
        const paragraphs = articleContainer.querySelectorAll('p');
        paragraphs[index].textContent = data.new_paragraph;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while regenerating the paragraph.');
    });
}

document.getElementById('aiGenerateImageButton').addEventListener('click', function() {
    const topic = document.getElementById('topic').value;
    if (!topic) {
        alert('Please enter a topic');
        return;
    }

    fetch('/generate_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        if (editorInstance && document.getElementById('editorContainer').style.display === 'block') {
            editorInstance.model.change(writer => {
                const insertPosition = editorInstance.model.document.selection.getFirstPosition();
                writer.insertElement('imageBlock', { src: data.image_url }, insertPosition);
            });
        } else {
            const articleContainer = document.getElementById('articleContainer');

            // Remove any existing images
            const existingImage = articleContainer.querySelector('img');
            if (existingImage) {
                existingImage.remove();
            }

            // Create a new image element
            const imgElement = document.createElement('img');
            imgElement.src = data.image_url;
            imgElement.alt = "Generated Image";
            imgElement.style.maxWidth = '100%';

            // Insert the image at the beginning of the container
            articleContainer.insertAdjacentElement('afterbegin', imgElement);
        }
    })
    .catch(error => {
        console.error('Error generating image:', error);
        alert('Error generating image: ' + error.message);
    });
});

document.getElementById('applyTemplateButton').addEventListener('click', function() {
    const selectedTemplate = document.querySelector('input[name="template"]:checked').value;
    const articleContainer = document.getElementById('articleContainer');
    const content = articleContainer.innerHTML;
    
    // Remove existing image and buttons
    const existingImage = articleContainer.querySelector('img');
    const imageSrc = existingImage ? existingImage.src : '';
    
    // Clear existing content
    articleContainer.innerHTML = '';

    if (selectedTemplate === 'template1') {
        // Apply Template 1
        articleContainer.innerHTML = `
            <div class="template1">
                ${content}
            </div>
        `;
    } else if (selectedTemplate === 'template2') {
        // Apply Template 2 with image
        articleContainer.innerHTML = `
            <div class="template2">
                ${content}
            </div>
        `;
    }

    // Remove any existing button containers from the new content
    const buttonContainers = articleContainer.querySelectorAll('.button-container');
    buttonContainers.forEach(buttonContainer => buttonContainer.remove());
});
