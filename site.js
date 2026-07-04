const filterButtons = document.querySelectorAll(".filter-button");
const reportCards = document.querySelectorAll(".report-card");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.toggle("active", item === button));
    reportCards.forEach((card) => {
      const category = card.dataset.category;
      card.hidden = filter !== "all" && category !== filter;
    });
  });
});
