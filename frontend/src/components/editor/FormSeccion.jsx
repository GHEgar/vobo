import { useState } from 'react';
import { ArrowLeft, Eye, History } from 'tesela/react';
import { Button } from '@/components/Button';
import { SelectField, TextField } from '@/components/Field';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { CasosSeccion } from '@/components/editor/CasosSeccion';
import { Historial } from '@/components/editor/Historial';
import { ResumenErrores } from '@/components/editor/ResumenErrores';
import { Herramientas, MediaGaleria, QueCambia } from '@/components/editor/ListasSeccion';
import { useCrearSeccion, useGuardarSeccion, useProcedimientosEditor, useSeccionEditor } from '@/hooks/useEditor';
import { claveDesde } from '@/utils/claves';
import { erroresDe, seccionVacia } from '@/utils/editor';
import { useRuta } from '@/hooks/useProyecto';

const AUDIENCIAS = [
    { valor: 'funcional', texto: 'Funcional' },
    { valor: 'tecnica', texto: 'Técnica' },
];

const Envoltura = ({ incrustado, onSubmit, children }) => (incrustado
    ? <form onSubmit={onSubmit} className="flex flex-col">{children}</form>
    : <Tarjeta as="form" onSubmit={onSubmit} className="flex flex-col">{children}</Tarjeta>);

const Formulario = ({ detalle, sistemas, procedimientos, crear, guardar, inicial, incrustado, onGuardada, onVolver }) => {
    const ruta = useRuta();
    const mutacion = detalle ? guardar : crear;
    const [datos, setDatos] = useState(detalle?.datos ?? { ...seccionVacia(sistemas[0]?.clave), ...inicial });
    const [idManual, setIdManual] = useState(false);
    const [historial, setHistorial] = useState(false);
    const errores = erroresDe(mutacion.error);
    const cambiar = (cambios) => setDatos({ ...datos, ...cambios });
    const texto = (nombre) => ({ value: datos[nombre] ?? '', error: errores.get(nombre), onChange: (e) => cambiar({ [nombre]: e.target.value }) });
    const guardados = (detalle?.datos.casos ?? []).map((c) => c.id);

    const enviar = (e) => {
        e.preventDefault();
        const opciones = { onSuccess: (respuesta) => onGuardada(respuesta.id) };
        if (detalle) guardar.mutate({ id: detalle.id, datos }, opciones);
        else crear.mutate(datos, opciones);
    };

    return (
        <Envoltura incrustado={incrustado} onSubmit={enviar}>
            {!incrustado && <div className="flex flex-wrap items-center justify-between gap-2">
                <Button label="Secciones" icono={<ArrowLeft size={16} />} variant="link" small onClick={onVolver} />
                {detalle && (
                    <div className="flex flex-wrap gap-2">
                        <Button label="Historial" icono={<History size={16} />} variant="ghost" small onClick={() => setHistorial(true)} />
                        {!detalle.datos.oculta && (
                            <a href={ruta(`/seccion/${encodeURIComponent(detalle.id)}`)} target="_blank" rel="noreferrer" className="inline-flex h-[30px] items-center gap-2 rounded-full border border-gris px-4 tipo-negrita text-xs text-texto-tenue hover:border-primario hover:text-primario">
                                <Eye size={16} /> Ver como validador
                            </a>
                        )}
                    </div>
                )}
            </div>}
            {!incrustado && <h2 className="mt-3 tipo-negrita text-lg text-texto">{detalle ? `Editar ${detalle.datos.titulo}` : 'Nueva sección'}</h2>}
            {detalle?.con_resultados && <p className="mt-1 tipo-media text-xs text-texto-apagado">Esta sección ya tiene resultados: sus casos con resultados conservan el id.</p>}
            <div className="grid gap-x-4 sm:grid-cols-2">
                <TextField
                    id="seccion-titulo"
                    label="Título"
                    required
                    {...texto('titulo')}
                    onChange={(e) => cambiar({ titulo: e.target.value, ...(detalle || idManual ? {} : { id: claveDesde(e.target.value, 120) }) })}
                />
                <TextField
                    id="seccion-id"
                    label="Id"
                    required
                    tooltip="Forma parte de la dirección de la sección. No cambia después de crearla."
                    disabled={Boolean(detalle)}
                    pattern="[a-z0-9][a-z0-9\-]{0,119}"
                    {...texto('id')}
                    onChange={(e) => {
                        setIdManual(true);
                        cambiar({ id: e.target.value });
                    }}
                />
                <div className="mt-4">
                    <SelectField id="seccion-sistema" label="Sistema" options={sistemas.map((p) => ({ valor: p.clave, texto: p.nombre }))} value={datos.sistema} onChange={(e) => cambiar({ sistema: e.target.value })} />
                    {errores.get('sistema') && <p className="mt-1 tipo-media text-xs text-error-fuerte">{errores.get('sistema')}</p>}
                </div>
                <div className="mt-4">
                    <SelectField id="seccion-audiencia" label="Audiencia" options={AUDIENCIAS} value={datos.audiencia ?? 'funcional'} onChange={(e) => cambiar({ audiencia: e.target.value })} />
                </div>
            </div>
            <TextField id="seccion-resumen" label="Resumen" multiline rows={3} {...texto('resumen')} />
            <TextField id="seccion-donde" label="Dónde" placeholder="Dirección donde se prueba" {...texto('donde')} />
            <QueCambia items={datos.que_cambia ?? []} onChange={(que_cambia) => cambiar({ que_cambia })} errores={errores} />
            <Herramientas items={datos.herramientas ?? []} onChange={(herramientas) => cambiar({ herramientas })} errores={errores} bloqueadas={detalle?.herramientas_bloqueadas ?? []} />
            <MediaGaleria items={datos.media ?? []} onChange={(media) => cambiar({ media })} errores={errores} procedimientos={procedimientos} />
            <CasosSeccion
                casos={datos.casos ?? []}
                herramientas={datos.herramientas ?? []}
                procedimientos={procedimientos}
                errores={errores}
                bloqueados={detalle?.casos_bloqueados ?? []}
                guardados={guardados}
                onChange={(casos) => cambiar({ casos })}
            />
            <ResumenErrores error={mutacion.error} />
            <div className="mt-6 flex flex-wrap items-center justify-end gap-3">
                {mutacion.isSuccess && !mutacion.isPending && <p role="status" className="tipo-media text-xs text-pasa">Guardado</p>}
                <Button label="Cancelar" variant="link" onClick={onVolver} />
                <Button label={detalle ? 'Guardar sección' : 'Crear sección'} type="submit" loading={mutacion.isPending} disabled={!datos.titulo?.trim() || !datos.id} />
            </div>
            {detalle && <Historial abierto={historial} tipo="seccion" id={detalle.id} titulo={detalle.datos.titulo} onCerrar={() => setHistorial(false)} />}
        </Envoltura>
    );
};

export const FormSeccion = ({ seccionId, sistemas, inicial, incrustado = false, onGuardada, onVolver }) => {
    const detalle = useSeccionEditor(seccionId);
    const procedimientos = useProcedimientosEditor();
    const crear = useCrearSeccion();
    const guardar = useGuardarSeccion();
    if ((seccionId && detalle.isPending) || procedimientos.isPending) return <Spinner />;
    if (detalle.error) return <ErrorState mensaje={detalle.error.message} onReintentar={detalle.refetch} />;
    return (
        <Formulario
            key={`${seccionId ?? 'nueva'}-${detalle.data?.actualizado ?? ''}`}
            detalle={seccionId ? detalle.data : null}
            sistemas={sistemas}
            procedimientos={procedimientos.data ?? []}
            crear={crear}
            guardar={guardar}
            inicial={inicial}
            incrustado={incrustado}
            onGuardada={onGuardada}
            onVolver={onVolver}
        />
    );
};
