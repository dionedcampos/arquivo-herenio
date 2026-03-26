/**
 * Real-time Archive Search logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const yearFilter = document.getElementById('year-filter');
    const postsGrid = document.getElementById('posts-grid');
    const postCards = document.querySelectorAll('.post-card');
    const noResults = document.getElementById('no-results');
    const postsCount = document.getElementById('posts-count');

    if (!searchInput || !postsGrid || !yearFilter) return;

    function filterPosts() {
        const query = searchInput.value.toLowerCase().trim();
        const selectedYear = yearFilter.value;
        let visibleCount = 0;

        postCards.forEach(card => {
            const title = card.getAttribute('data-title') || '';
            const year = card.getAttribute('data-year') || '';

            const matchesSearch = title.includes(query);
            const matchesYear = selectedYear === '' || year === selectedYear;

            if (matchesSearch && matchesYear) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Update count and no results message
        if (visibleCount === 0) {
            postsGrid.style.display = 'none';
            noResults.style.display = 'block';
        } else {
            postsGrid.style.display = 'grid';
            noResults.style.display = 'none';
        }

        postsCount.textContent = `${visibleCount} post${visibleCount !== 1 ? 's' : ''}`;
    }

    searchInput.addEventListener('input', filterPosts);
    yearFilter.addEventListener('change', filterPosts);

    // Initial run to ensure correct state on load
    filterPosts();
    console.log(`Search initialized with ${postCards.length} cards.`);
});
