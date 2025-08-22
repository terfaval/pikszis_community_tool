function flipCard(slug) {
  const card = document.querySelector(`.card[data-slug="${slug}"]`);
  if (card) {
    card.classList.toggle('card-flipped');
  }
}