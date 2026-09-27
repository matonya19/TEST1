export function matchesFilters(post, { activeProjectId, search, filters }) {
  if (activeProjectId !== 'all' && post.projectId !== activeProjectId) return false;
  if (filters.platforms.length && !filters.platforms.includes(post.platform)) return false;
  if (filters.formats.length && !filters.formats.includes(post.format)) return false;
  if (filters.statuses.length && !filters.statuses.includes(post.status)) return false;
  if (search && search.trim()) {
    const q = search.trim().toLowerCase();
    const hay = `${post.topic} ${post.text} ${post.notes}`.toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

export function visiblePosts(posts, pendingDeleteIds) {
  return posts.filter((p) => !pendingDeleteIds.has(p.id));
}
