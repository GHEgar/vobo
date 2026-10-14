import { useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Tarjeta } from '@/components/Tarjeta';
import { FallaForm } from '@/components/caso/FallaForm';
import { ComentarioPaso } from '@/components/caso/ComentarioPaso';
import { ComentariosCaso } from '@/components/caso/ComentariosCaso';
import { CopiarContrasena } from '@/components/caso/CopiarContrasena';
import { CuentasPrueba } from '@/components/inicio/CuentasPrueba';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { PasoActual } from '@/components/caso/PasoActual';
import { useCasoGuiado } from '@/hooks/useCasoGuiado';
import { useProgreso } from '@/hooks/useMisCasos';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';
import { estadoDe } from '@/utils/progreso';

const PLANTILLA = 'Qué hice: \nQué vi: \nQué esperaba: \n';

const Bloque = ({ titulo, children }) => (
    <div>
        <h2 className="tipo-negrita text-sm text-texto">{titulo}</h2>
        <div className="mt-1 tipo-media text-sm/6 text-texto-tenue">{children}</div>
    </div>
);

const siguientePendiente = (datos, casoId) => {
    const audiencia = datos.indice.secciones.get(datos.indice.casos.get(casoId)?.seccionId)?.audiencia;
    const casos = datos.casos.filter((c) => datos.indice.secciones.get(c.seccionId)?.audiencia === audiencia);
    const posicion = casos.findIndex((c) => c.id === casoId);
    const despues = [...casos.slice(posicion + 1), ...casos.slice(0, Math.max(posicion, 0))];
    return despues.find((c) => c.id !== casoId && estadoDe(datos.estados, c.id) === 'pendiente') ?? null;
};

const pasoDeUrl = (valor, total) => {
    const numero = Number(valor);
    return Number.isInteger(numero) && numero >= 1 && numero <= total ? numero - 1 : null;
};

const SIN_CUENTA = new Set(['', 'ninguna', '—']);

const Cabecera = ({ caso, contador }) => (
    <div className="flex flex-col gap-2 md:flex-row-reverse md:items-start md:justify-between md:gap-6">
        <div className="flex shrink-0 flex-wrap items-center gap-2 md:pt-2">
            <span className="tipo-media text-xs text-texto-apagado">{caso.id}</span>
            {contador && <span className="tipo-negrita text-xs text-primario">{contador}</span>}
        </div>
        <h1 className="tipo-negrita text-xl text-texto md:text-2xl">{caso.titulo}</h1>
    </div>
);

const Preparacion = ({ caso }) => (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {caso.antes && <Bloque titulo="Antes de empezar"><TextoConEnlaces texto={caso.antes} /></Bloque>}
        <Bloque titulo="Con qué cuenta">
            <span className="flex flex-wrap items-center gap-x-3 gap-y-2">
                <span>{caso.cuenta || '—'}{caso.rol && <span className="text-texto-apagado"> · {caso.rol}</span>}</span>
                {!SIN_CUENTA.has((caso.cuenta ?? '').trim().toLowerCase()) && <CuentasPrueba etiqueta="Cuentas de prueba" resaltar={caso.cuenta} />}
                <CopiarContrasena cuenta={caso.cuenta} />
            </span>
        </Bloque>
    </div>
);

const CasoGuia = ({ caso, datos, ronda, pedidoFuera, pasoPedido }) => {
    const { usuario, puede } = useSesion();
    const resultado = datos.estados.get(caso.id);
    const siguiente = siguientePendiente(datos, caso.id);
    const guia = useCasoGuiado({ caso, ronda, resultado, siguiente, pasoPedido });
    const editable = puede(PERMISOS.ejecutarCasos) && ronda?.abierta;
    const { setModo } = guia;

    useEffect(() => {
        if (pedidoFuera && editable) setModo('otro');
    }, [pedidoFuera, editable, setModo]);
    const respuesta = guia.pasos.find((p) => p.paso === guia.actual);

    useEffect(() => {
        if (['falla', 'comentario', 'otro'].includes(guia.modo)) {
            document.getElementById('accion-paso')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, [guia.modo]);
    const estado = resultado?.estado ?? 'pendiente';
    const contador = guia.terminado ? null : `Paso ${guia.actual + 1} de ${caso.pasos.length}`;

    return (
        <>
            <Tarjeta className="flex flex-col gap-5 pb-4 md:pb-5">
                <div>
                    <Cabecera caso={caso} contador={contador} />
                </div>
                {guia.terminado ? (
                    <p role="status" className="rounded-2xl bg-pasa-fondo px-5 py-4 tipo-negrita text-sm text-pasa">
                        {siguiente ? 'Caso guardado · siguiente…' : 'Caso guardado. Terminaste todos tus casos de esta ronda.'}
                    </p>
                ) : (
                    <PasoActual
                        caso={caso}
                        indice={guia.actual}
                        procedimiento={datos.indice.procedimientos.get(caso.pasos[guia.actual].procedimiento)}
                        elegido={respuesta?.estado ?? (guia.actual === caso.pasos.length - 1 && estado !== 'pendiente' ? estado : null)}
                        modo={guia.modo}
                        onModo={guia.setModo}
                        onResponder={guia.responder}
                        editable={editable}
                        guardando={guia.guardar.isPending}
                    />
                )}
                {guia.guardar.error && <p className="tipo-media text-sm text-error-fuerte">{guia.guardar.error.message}</p>}
            </Tarjeta>
            {!guia.terminado && guia.modo === 'comentario' && (
                <Tarjeta id="accion-paso" className="scroll-mt-32">
                    <h2 className="mb-1 tipo-negrita text-lg text-texto">Comentario sobre el paso {guia.actual + 1}</h2>
                    <ComentarioPaso
                        id={`comentario-${guia.actual}`}
                        label="Qué hiciste, qué viste y qué esperabas"
                        inicial={respuesta?.comentario || PLANTILLA}
                        requerido
                        filas={4}
                        accion="Guardar y seguir"
                        guardando={guia.guardar.isPending}
                        onCancelar={() => guia.setModo('botones')}
                        onGuardar={(texto) => guia.responder('comentario', texto)}
                    />
                </Tarjeta>
            )}
            {!guia.terminado && guia.modo === 'falla' && (
                <Tarjeta id="accion-paso" className="scroll-mt-32">
                    <FallaForm
                        caso={caso}
                        ronda={ronda}
                        usuario={usuario}
                        paso={guia.actual}
                        onCancelar={() => guia.setModo('botones')}
                        onEnviada={(tipo) => guia.responder(tipo === 'no_pude' ? 'no_pude' : 'falla', null)}
                    />
                </Tarjeta>
            )}
            {!guia.terminado && guia.modo === 'otro' && (
                <Tarjeta id="accion-paso" className="scroll-mt-32">
                    <FallaForm
                        caso={caso}
                        ronda={ronda}
                        usuario={usuario}
                        paso={null}
                        onCancelar={() => guia.setModo('botones')}
                        onEnviada={() => guia.setModo('enviado')}
                    />
                </Tarjeta>
            )}
            {guia.modo === 'enviado' && (
                <p role="status" className="rounded-2xl bg-pasa-fondo px-5 py-4 tipo-negrita text-sm text-pasa">
                    Reporte enviado. Sigue con el paso {guia.actual + 1}.
                </p>
            )}
            <ComentariosCaso casoId={caso.id} rondaId={ronda.id} deTodos={puede(PERMISOS.gestionarFallas)} />
        </>
    );
};

const Caso = () => {
    const { casoId } = useParams();
    const [params] = useSearchParams();
    const { ronda, datos, cargando, error, reintentar } = useProgreso();
    const [verPreparacion, setVerPreparacion] = useState(false);
    const [pedidoFuera, setPedidoFuera] = useState(0);

    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} />;
    const caso = datos.indice.casos.get(casoId);
    if (!caso) return <EmptyState titulo="Caso no encontrado" />;
    const seccion = datos.indice.secciones.get(caso.seccionId);
    const pasoPedido = pasoDeUrl(params.get('paso'), caso.pasos.length);

    return (
        <>
            <div className="flex flex-wrap items-center justify-between gap-3">
                <Link to={`/seccion/${seccion.id}`} className="w-fit tipo-negrita text-sm text-primario hover:underline">‹ {seccion.titulo}</Link>
                <div className="flex flex-wrap items-center gap-2">
                    {ronda && <Button label="Algo fuera de los pasos" small variant="ghost" onClick={() => setPedidoFuera((n) => n + 1)} />}
                    <CuentasPrueba etiqueta="Cuentas de prueba" resaltar={caso.cuenta} />
                    <Button label="Antes de empezar" small variant="ghost" onClick={() => setVerPreparacion(true)} />
                </div>
            </div>
            <Modal abierto={verPreparacion} titulo="Preparación" onCerrar={() => setVerPreparacion(false)}>
                <Preparacion caso={caso} />
            </Modal>
            {ronda ? <CasoGuia key={`${ronda.id}-${caso.id}-${pasoPedido ?? ''}`} caso={caso} datos={datos} ronda={ronda} pedidoFuera={pedidoFuera} pasoPedido={pasoPedido} /> : <EmptyState titulo="No hay una ronda abierta" />}
        </>
    );
};

export default Caso;
