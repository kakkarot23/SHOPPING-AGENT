// AI Shopping Agent JavaScript Engine
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Shopping Agent initialized.');

    // 1. Conversational Chat Engine
    const chatInput = document.getElementById('chat-input-field');
    const sendBtn = document.getElementById('chat-send-btn');
    const chatBox = document.getElementById('chat-messages-container');

    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', handleSendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSendMessage();
        });
    }

    async function handleSendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Append user message
        appendChatBubble(text, 'user');
        chatInput.value = '';

        // Append loading indicator
        const loadingBubble = appendChatBubble('🤖 Analyzing intent & searching marketplace...', 'ai loading');

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            loadingBubble.remove();

            // Append AI response
            appendChatBubble(data.reply, 'ai');

            // If products returned, append product cards grid to chat
            if (data.products && data.products.length > 0) {
                const gridHtml = document.createElement('div');
                gridHtml.className = 'grid-3';
                gridHtml.style.marginTop = '12px';

                data.products.forEach(p => {
                    gridHtml.innerHTML += `
                        <div class="product-card" style="padding: 12px; background: rgba(0,0,0,0.3);">
                            <img src="${p.image_url}" style="height:120px; object-fit:cover; border-radius:8px;" alt="${p.title}" />
                            <div style="margin-top:8px;">
                                <span class="badge badge-overall">${p.badge || 'AI Pick'}</span>
                                <h4 style="font-size:0.9rem; margin:6px 0; color:#fff;">${p.title}</h4>
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="color:var(--primary-cyan); font-weight:bold;">₹${p.price.toLocaleString()}</span>
                                    <a href="/product/${p.slug}/" class="btn-outline" style="padding:4px 8px; font-size:0.75rem;">View</a>
                                </div>
                            </div>
                        </div>
                    `;
                });
                chatBox.appendChild(gridHtml);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        } catch (err) {
            loadingBubble.textContent = "❌ Error processing request. Please try again.";
        }
    }

    function appendChatBubble(text, sender) {
        if (!chatBox) return;
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        bubble.innerHTML = text;
        chatBox.appendChild(bubble);
        chatBox.scrollTop = chatBox.scrollHeight;
        return bubble;
    }

    // 2. Wishlist & Cart Actions
    window.toggleWishlist = async function(productId, btn) {
        try {
            const res = await fetch('/api/wishlist/toggle/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });
            const data = await res.json();
            if (data.status === 'added') {
                btn.style.color = '#FF0844';
                btn.innerHTML = '<i class="fa-solid fa-heart"></i> Saved';
            } else {
                btn.style.color = 'var(--text-muted)';
                btn.innerHTML = '<i class="fa-regular fa-heart"></i> Wishlist';
            }
        } catch (e) {
            console.error(e);
        }
    };

    window.addToCart = async function(productId, btn) {
        try {
            const res = await fetch('/api/cart/add/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });
            const data = await res.json();
            if (data.status === 'added') {
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Added to Cart';
                btn.style.background = 'var(--accent-emerald)';
            }
        } catch (e) {
            console.error(e);
        }
    };

    // Quick Prompt Filler
    window.useSamplePrompt = function(promptText) {
        if (chatInput) {
            chatInput.value = promptText;
            handleSendMessage();
        }
    };
});
