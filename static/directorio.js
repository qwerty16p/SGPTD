const menu = document.querySelector("#menu");
menu?.addEventListener("click", () => {
    const nav = document.querySelector("#nav");
    nav.hidden = !nav.hidden;
    menu.setAttribute("aria-expanded", String(!nav.hidden));
});
document.querySelector("#abrir")?.addEventListener("click", () => document.querySelector("#selector").showModal());
const filtro = document.querySelector("#filtro");
if (filtro) {
    const select = document.querySelector("select[name=aplicacion]");
    const opciones = Array.from(select.options);
    filtro.addEventListener("input", () => {
        const consulta = filtro.value.trim().toLocaleLowerCase();
        select.replaceChildren(...opciones.filter(op => op.text.toLocaleLowerCase().includes(consulta)));
        select.selectedIndex = select.options.length === 1 ? 0 : -1;
    });
}
document.querySelectorAll("form[data-confirm]").forEach(form => {
    form.addEventListener("submit", event => {
        if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
});
