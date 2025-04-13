document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blogGenerationForm');
    const blogResult = document.getElementById('blogResult');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');

    // Function to update word count
    function updateWordCount() {
        const draftContent = document.getElementById('draftEditor').textContent;
        const wordCount = draftContent.trim().split(/\s+/).length;
        document.getElementById('currentWordCount').textContent = `${wordCount} words`;
    }

    // Function to render keywords
    function renderKeywords(container, keywords) {
        const div = document.getElementById(container);
        div.innerHTML = '';
        keywords.forEach(keyword => {
            const span = document.createElement('span');
            span.className = 'keyword-tag';
            span.textContent = keyword;
            div.appendChild(span);
        });
    }

    // Function to render SEO recommendations
    function renderSEORecommendations(recommendations) {
        // Internal Linking
        const internalLinking = document.getElementById('internalLinking');
        internalLinking.innerHTML = recommendations.internal_linking.map(link => 
            `<li class="mb-2">
                <i class="fas fa-arrow-right text-primary me-2"></i>${link}
             </li>`
        ).join('');

        // Featured Snippet Opportunities
        const snippetOpportunities = document.getElementById('snippetOpportunities');
        snippetOpportunities.innerHTML = recommendations.featured_snippet_opportunities.map(opportunity => 
            `<li class="mb-2">
                <i class="fas fa-lightbulb text-warning me-2"></i>${opportunity}
             </li>`
        ).join('');

        // Content Gaps
        const contentGaps = document.getElementById('contentGaps');
        contentGaps.innerHTML = recommendations.content_gaps.map(gap => 
            `<li class="mb-2">
                <i class="fas fa-exclamation-circle text-danger me-2"></i>${gap}
             </li>`
        ).join('');
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            loadingSpinner.style.display = 'block';
            blogResult.style.display = 'none';
            successMessage.style.display = 'none';
            
            try {
                // Get form data
                const formData = new FormData(form);
                const topic = formData.get('topic');
                const tone = formData.get('tone');
                const keywords = formData.get('keywords');
                const selectedDocs = Array.from(formData.getAll('selected_documents'));
                
                // Make API request
                const response = await fetch('/generate-blog/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        topic: topic,
                        tone: tone,
                        keywords: keywords,
                        document_ids: selectedDocs
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to generate blog');
                }
                
                const data = await response.json();
                
                // Update UI with generated content
                document.getElementById('blogTitle').textContent = data.blog_title;
                document.getElementById('metaDescription').textContent = data.meta_description;
                document.getElementById('wordCountRecommendation').textContent = `Recommended length: ${data.word_count}`;
                
                // Render keywords
                renderKeywords('targetKeywords', data.keywords.user_keywords);
                renderKeywords('aiKeywords', data.keywords.additional_keywords);
                renderKeywords('lsiKeywords', data.keywords.lsi_keywords);
                renderKeywords('semanticVariations', data.keywords.semantic_variations);
                
                // Render outline and draft
                document.getElementById('outlineEditor').innerHTML = data.blog_outline;
                document.getElementById('draftEditor').innerHTML = data.blog_draft;
                
                // Render SEO recommendations
                renderSEORecommendations(data.seo_recommendations);
                
                // Update word count
                updateWordCount();
                
                // Show success state
                blogResult.style.display = 'block';
                successMessage.textContent = 'Blog generated successfully!';
                successMessage.style.display = 'block';
                
                // Scroll to results
                blogResult.scrollIntoView({ behavior: 'smooth' });
                
            } catch (error) {
                console.error('Error:', error);
                successMessage.textContent = 'Error generating blog. Please try again.';
                successMessage.style.display = 'block';
                successMessage.className = 'alert alert-danger';
            } finally {
                loadingSpinner.style.display = 'none';
            }
        });
    }

    // Add event listeners for content changes
    const draftEditor = document.getElementById('draftEditor');
    if (draftEditor) {
        draftEditor.addEventListener('input', updateWordCount);
    }

    // Grammar check functionality
    const checkGrammarBtn = document.getElementById('checkGrammarBtn');
    if (checkGrammarBtn) {
        checkGrammarBtn.addEventListener('click', async function() {
            const draftContent = document.getElementById('draftEditor').innerHTML;
            const button = this;
            const originalText = button.innerHTML;
            
            try {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Checking...';
                
                const response = await fetch('/check-grammar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ text: draftContent })
                });
                
                if (!response.ok) {
                    throw new Error('Grammar check failed');
                }
                
                const data = await response.json();
                
                // Apply grammar suggestions
                let content = draftContent;
                data.suggestions.forEach(suggestion => {
                    const span = document.createElement('span');
                    span.className = 'grammar-suggestion';
                    span.title = suggestion.message;
                    span.setAttribute('data-replacements', JSON.stringify(suggestion.replacements));
                    
                    const text = content.substring(suggestion.from, suggestion.to);
                    span.textContent = text;
                    
                    content = content.substring(0, suggestion.from) + 
                             span.outerHTML + 
                             content.substring(suggestion.to);
                });
                
                document.getElementById('draftEditor').innerHTML = content;
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error checking grammar. Please try again.');
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        });
    }

    // Save changes functionality
    const saveChangesBtn = document.getElementById('saveChangesBtn');
    if (saveChangesBtn) {
        saveChangesBtn.addEventListener('click', async function() {
            const button = this;
            const originalText = button.innerHTML;
            
            try {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
                
                const blogData = {
                    blog_title: document.getElementById('blogTitle').textContent,
                    meta_description: document.getElementById('metaDescription').textContent,
                    blog_outline: document.getElementById('outlineEditor').innerHTML,
                    blog_draft: document.getElementById('draftEditor').innerHTML
                };
                
                const response = await fetch('/save-blog/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(blogData)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save blog');
                }
                
                const data = await response.json();
                
                // Show success message
                successMessage.textContent = 'Blog saved successfully!';
                successMessage.className = 'alert alert-success';
                successMessage.style.display = 'block';
                
                // Redirect to blogs list after a short delay
                setTimeout(() => {
                    window.location.href = '/blogs/';
                }, 1500);
                
            } catch (error) {
                console.error('Error:', error);
                successMessage.textContent = 'Error saving blog. Please try again.';
                successMessage.className = 'alert alert-danger';
                successMessage.style.display = 'block';
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        });
    }
}); 