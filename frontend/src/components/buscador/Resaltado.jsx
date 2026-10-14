import { highlight } from '@ghegar/muestrario';

const segmentar = (texto, consulta) => {
    const letras = Array.from(texto);
    const marcadas = new Array(letras.length).fill(false);
    consulta.split(/\s+/).filter(Boolean).forEach((palabra) => {
        let posicion = 0;
        highlight(texto, palabra).forEach((segmento) => {
            const largo = Array.from(segmento.text).length;
            if (segmento.match) marcadas.fill(true, posicion, posicion + largo);
            posicion += largo;
        });
    });
    return letras.reduce((segmentos, letra, i) => {
        const ultimo = segmentos.at(-1);
        if (ultimo && ultimo.marca === marcadas[i]) ultimo.texto += letra;
        else segmentos.push({ texto: letra, marca: marcadas[i] });
        return segmentos;
    }, []);
};

export const Resaltado = ({ texto, consulta }) => segmentar(texto, consulta).map((s, i) => (
    s.marca
        ? <mark key={i} className="rounded-sm bg-aviso-fondo text-texto">{s.texto}</mark>
        : <span key={i}>{s.texto}</span>
));
