const PATRON = /(https?:\/\/[^\s«»<>"]+)/g;
const PUNTUACION_FINAL = /[.,;:!?)]+$/;

const partir = (texto) => texto.split(PATRON).flatMap((parte, i) => {
    if (i % 2 === 0) return parte ? [{ texto: parte }] : [];
    const sobrante = parte.match(PUNTUACION_FINAL)?.[0] ?? '';
    const url = sobrante ? parte.slice(0, -sobrante.length) : parte;
    return sobrante ? [{ url }, { texto: sobrante }] : [{ url }];
});

export const TextoConEnlaces = ({ texto }) => {
    if (!texto) return null;
    return partir(texto).map((parte, i) => (parte.url ? (
        <a key={i} href={parte.url} target="_blank" rel="noopener noreferrer" className="break-all text-primario underline underline-offset-2 hover:text-primario-hover">
            {parte.url}
        </a>
    ) : (
        <span key={i}>{parte.texto}</span>
    )));
};
