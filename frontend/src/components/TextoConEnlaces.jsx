const PATRON = /(https?:\/\/[^\s«»<>"]+)/g;
const PUNTUACION_FINAL = /[.,;:!?)]+$/;
const MAXIMO = 48;

const partir = (texto) => texto.split(PATRON).flatMap((parte, i) => {
    if (i % 2 === 0) return parte ? [{ texto: parte }] : [];
    const sobrante = parte.match(PUNTUACION_FINAL)?.[0] ?? '';
    const url = sobrante ? parte.slice(0, -sobrante.length) : parte;
    return sobrante ? [{ url }, { texto: sobrante }] : [{ url }];
});

const acortar = (url) => {
    if (url.length <= MAXIMO) return url;
    try {
        const { host, pathname, search, hash } = new URL(url);
        const visible = `${host}${pathname === '/' ? '' : pathname}`;
        if (visible.length > MAXIMO) return `${visible.slice(0, MAXIMO - 1)}…`;
        return search || hash ? `${visible}…` : visible;
    } catch {
        return `${url.slice(0, MAXIMO - 1)}…`;
    }
};

export const TextoConEnlaces = ({ texto }) => {
    if (!texto) return null;
    return partir(texto).map((parte, i) => (parte.url ? (
        <a key={i} href={parte.url} title={parte.url} target="_blank" rel="noopener noreferrer" className="wrap-anywhere text-primario underline underline-offset-2 hover:text-primario-hover">
            {acortar(parte.url)}
        </a>
    ) : (
        <span key={i}>{parte.texto}</span>
    )));
};
