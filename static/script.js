/* apply saved theme early */
if (localStorage.getItem("theme") === "light") {
    document.documentElement.classList.add("light-theme");
}

/* get all toggle buttons */
const buttons = document.querySelectorAll(".theme-toggle");

/* update icons on all toggles */
function setIcons() {
    const icon = document.documentElement.classList.contains("light-theme")
        ? "☀️"
        : "🌙";

    buttons.forEach(btn => btn.textContent = icon);
}

setIcons();

/* attach toggle handler to every button (mobile + desktop) */
buttons.forEach(btn => {
    btn.addEventListener("click", () => {
        document.documentElement.classList.toggle("light-theme");

        const isLight =
            document.documentElement.classList.contains("light-theme");

        localStorage.setItem("theme", isLight ? "light" : "dark");

        setIcons();
    });
});
