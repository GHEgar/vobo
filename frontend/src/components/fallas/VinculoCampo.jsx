import { useMemo } from 'react';
import { createPortal } from 'react-dom';
import { useCombobox } from '@ghegar/muestrario';
import { Button } from '@/components/Button';
import { CLASE_CAMPO } from '@/components/Field';
import { Label } from '@/components/Label';
import { Resaltado } from '@/components/buscador/Resaltado';
import { useComentarios, useFallas } from '@/hooks/useValidacion';
import { etiquetaComentario, etiquetaFalla } from '@/utils/seguimiento';

const GRUPOS = { falla: 'Fallas', comentario: 'Comentarios' };
const SIN_FILTROS = {};
const ALTO_MAXIMO = 320;

const ETIQUETAS = {
    noResults: 'Sin reportes que coincidan',
    loading: 'Cargando…',
    error: 'No se pudo cargar',
    clear: 'Limpiar',
    remove: 'Quitar',
    typeMore: (n) => `Escribe al menos ${n} caracteres`,
    results: (n) => `${n} ${n === 1 ? 'reporte' : 'reportes'}`,
};

const clave = (o) => `${o.objeto}:${o.id}`;

const candidatos = (fallas, comentarios) => [
    ...fallas.map((f) => ({ objeto: 'falla', id: f.id, etiqueta: etiquetaFalla(f), titulo: f.seccion_completa ? f.seccion_titulo : f.caso_titulo, principal: f.principal })),
    ...comentarios.filter((c) => c.id != null).map((c) => ({ objeto: 'comentario', id: c.id, etiqueta: etiquetaComentario(c), titulo: c.caso_titulo, principal: c.principal })),
];

const Lista = ({ combo }) => {
    const props = combo.getListboxProps();
    const alto = Math.min(combo.position?.availableHeight ?? ALTO_MAXIMO, ALTO_MAXIMO);
    return createPortal(
        <div {...props} data-emergente-anidado="" style={{ ...props.style, maxHeight: alto }} className="z-[60] overflow-y-auto rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)]">
            {!combo.items.length && combo.statusText && <p aria-hidden="true" className="px-3 py-2 tipo-media text-sm text-texto-apagado">{combo.statusText}</p>}
            {combo.groups?.map((grupo) => (
                <div key={grupo.label} {...combo.getGroupProps(grupo)} className="py-1">
                    <div {...combo.getGroupLabelProps(grupo)} className="px-3 pb-1 tipo-negrita text-[11px] tracking-wide text-texto-apagado uppercase">{grupo.label}</div>
                    {grupo.options.map(({ item, index }) => (
                        <div key={clave(item)} {...combo.getOptionProps(item, index)} className="cursor-pointer rounded-xl px-3 py-1.5 data-[active]:bg-primario-claro data-[selected]:tipo-negrita">
                            <p className="truncate tipo-negrita text-xs text-texto"><Resaltado texto={item.etiqueta} consulta={combo.inputValue} /></p>
                            {item.titulo && <p className="truncate tipo-media text-xs text-texto-apagado"><Resaltado texto={item.titulo} consulta={combo.inputValue} /></p>}
                        </div>
                    ))}
                </div>
            ))}
        </div>,
        document.body,
    );
};

const Selector = ({ objeto, registro, onCambiar }) => {
    const { data: fallas = [] } = useFallas(SIN_FILTROS);
    const { data: comentarios = [] } = useComentarios('');
    const propio = clave({ objeto, id: registro.id });
    const opciones = useMemo(
        () => candidatos(fallas, comentarios).filter((o) => clave(o) !== propio && !o.principal),
        [fallas, comentarios, propio],
    );
    const actual = registro.principal ? opciones.find((o) => clave(o) === clave(registro.principal)) ?? null : null;
    const combo = useCombobox({
        items: opciones,
        getLabel: (o) => `${o.etiqueta} · ${o.titulo}`,
        getKey: clave,
        groupBy: (o) => GRUPOS[o.objeto],
        value: actual,
        onChange: (o) => o && clave(o) !== clave(registro.principal ?? {}) && onCambiar({ principal: { objeto: o.objeto, id: o.id } }),
        labels: ETIQUETAS,
    });
    const entrada = combo.getInputProps();

    return (
        <>
            <Label htmlFor={entrada.id} text="Se resuelve con" tooltip="Otro reporte que lo resuelve. Toma su plazo y sigue sus cambios de estado; no cuenta en las sumas de esfuerzo." />
            <div {...combo.getAnchorProps()} className="mt-3">
                <input {...entrada} placeholder={registro.principal?.etiqueta ?? 'Número, caso o título'} className={`h-[40px] ${CLASE_CAMPO}`} />
            </div>
            {combo.open && <Lista combo={combo} />}
            <span className="sr-only" {...combo.getStatusProps()}>{combo.statusText}</span>
        </>
    );
};

export const VinculoCampo = ({ objeto, registro, editable, onCambiar }) => {
    const seguidores = registro.seguidores ?? 0;
    if (!editable || seguidores > 0) {
        return (
            <div className="min-w-0">
                <Label as="p" text="Se resuelve con" />
                <p className={`mt-3 tipo-negrita text-sm ${registro.principal ? 'text-texto' : 'text-texto-apagado'}`}>{registro.principal?.etiqueta ?? 'Ningún otro reporte'}</p>
                {seguidores > 0 && <p className="mt-1 tipo-media text-xs text-texto-tenue">Lo {seguidores === 1 ? 'sigue 1 reporte' : `siguen ${seguidores} reportes`}: no puede seguir a otro.</p>}
            </div>
        );
    }
    return (
        <div className="min-w-0">
            <Selector objeto={objeto} registro={registro} onCambiar={onCambiar} />
            {registro.principal && (
                <div className="mt-2">
                    <Button label="Quitar vínculo" variant="link" small className="px-0" onClick={() => onCambiar({ principal: null })} />
                </div>
            )}
        </div>
    );
};
