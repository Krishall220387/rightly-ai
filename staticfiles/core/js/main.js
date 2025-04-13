document.addEventListener('DOMContentLoaded', function() {
    // Function to format blog content
    function formatBlogContent(content) {
        try {
            // Parse content if it's a string
            if (typeof content === 'string') {
                content = JSON.parse(content);
            }

            // Initialize HTML array with container
            let html = ['<div class="content-container">'];
            
            // Format Introduction
            if (content.introduction) {
                const introContent = typeof content.introduction === 'object' ? 
                    content.introduction.content : content.introduction;
                html.push(`
                    <div class="section introduction-section">
                        <h2 class="section-title">Introduction</h2>
                        <div class="section-content">${introContent}</div>
                    </div>
                `);
            }

            // Format Main Sections (H2)
            const mainSections = Object.entries(content)
                .filter(([key]) => /^H2_\d+$/.test(key))
                .sort((a, b) => {
                    const aNum = parseInt(a[0].split('_')[1]);
                    const bNum = parseInt(b[0].split('_')[1]);
                    return aNum - bNum;
                });

            mainSections.forEach(([h2Key, h2Value]) => {
                const h2Content = typeof h2Value === 'object' ? h2Value.content : h2Value;
                
                // Start main section
                html.push(`
                    <div class="section main-section">
                        <h2 class="section-title">${h2Content}</h2>
                `);

                // Find and format subsections (H3)
                const subsections = Object.entries(content)
                    .filter(([key]) => key.startsWith(`${h2Key}_`))
                    .sort((a, b) => {
                        const aNum = parseInt(a[0].split('_')[2]);
                        const bNum = parseInt(b[0].split('_')[2]);
                        return aNum - bNum;
                    });

                subsections.forEach(([h3Key, h3Value]) => {
                    const h3Content = typeof h3Value === 'object' ? h3Value.content : h3Value;
                    html.push(`
                        <div class="subsection">
                            <h3 class="subsection-title">${h3Content}</h3>
                            ${typeof h3Value === 'object' && h3Value.content ? 
                                `<div class="subsection-content">${h3Value.content}</div>` : ''}
                        </div>
                    `);
                });

                // Close main section
                html.push('</div>');
            });

            // Format Conclusion
            if (content.conclusion) {
                const conclusionContent = typeof content.conclusion === 'object' ? 
                    content.conclusion.content : content.conclusion;
                html.push(`
                    <div class="section conclusion-section">
                        <h2 class="section-title">Conclusion</h2>
                        <div class="section-content">${conclusionContent}</div>
                    </div>
                `);
            }

            // Close container
            html.push('</div>');
            return html.join('\n');
        } catch (error) {
            console.error('Error formatting blog content:', error);
            return `<div class="error-message">Error formatting content: ${error.message}</div>`;
        }
    }

    // Function to update the preview
    function updatePreview() {
        const outlineElement = document.getElementById('outlineEditor');
        const draftElement = document.getElementById('draftEditor');
        
        if (outlineElement) {
            try {
                const outlineContent = outlineElement.textContent.trim();
                if (outlineContent) {
                    outlineElement.innerHTML = formatBlogContent(outlineContent);
                }
            } catch (error) {
                console.error('Error updating outline preview:', error);
            }
        }
        
        if (draftElement) {
            try {
                const draftContent = draftElement.textContent.trim();
                if (draftContent) {
                    draftElement.innerHTML = formatBlogContent(draftContent);
                }
            } catch (error) {
                console.error('Error updating draft preview:', error);
            }
        }
    }

    // Initialize the preview
    updatePreview();

    // Add event listeners for any interactive elements
    const saveButton = document.querySelector('.save-changes');
    if (saveButton) {
        saveButton.addEventListener('click', function(e) {
            e.preventDefault();
            // Add your save logic here
            console.log('Save changes clicked');
        });
    }
}); 