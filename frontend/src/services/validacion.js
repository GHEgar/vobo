import { consulta, solicitar } from '@/services/api';
import {
    actividadSchema,
    avisoSchema,
    avisosSchema,
    contenidoSchema,
    instanciaSchema,
    noLeidosSchema,
    personasAvisoSchema,
    presenciasSchema,
    proyectosSchema,
    resultadosBusquedaSchema,
    resumenActividadSchema,
    sesionSchema,
} from '@/services/esquemas';

export const fetchInstancia = async (proyecto) => instanciaSchema.parse(await solicitar(`/instancia${consulta({ proyecto })}`));
export const fetchVersion = () => solicitar('/version');
export const fetchModo = () => solicitar('/auth/modo');
export const fetchSesion = async () => sesionSchema.parse(await solicitar('/auth/me'));
export const fetchUsuariosLocales = () => solicitar('/auth/usuarios-locales');
export const entrarLocal = (clave) => solicitar('/auth/local', { method: 'POST', json: { clave } });
export const salir = () => solicitar('/auth/logout', { method: 'POST' });
export const entrarCuenta = (datos) => solicitar('/auth/entrar', { method: 'POST', json: datos });
export const fetchInvitacion = (token) => solicitar(`/auth/invitacion/${encodeURIComponent(token)}`);
export const aceptarInvitacion = ({ token, ...datos }) => solicitar(
    `/auth/invitacion/${encodeURIComponent(token)}`,
    { method: 'POST', json: datos },
);
export const fetchRestablecimiento = (token) => solicitar(`/auth/restablecer/${encodeURIComponent(token)}`);
export const restablecer = ({ token, ...datos }) => solicitar(
    `/auth/restablecer/${encodeURIComponent(token)}`,
    { method: 'POST', json: datos },
);
export const cambiarContrasena = (datos) => solicitar('/auth/contrasena', { method: 'POST', json: datos });

export const fetchProyectos = async () => proyectosSchema.parse(await solicitar('/proyectos'));

export const fetchContenido = async (proyecto) => contenidoSchema.parse(await solicitar(`/contenido${consulta({ proyecto })}`));

export const buscar = async (q, rondaId, proyecto, signal) => resultadosBusquedaSchema.parse(await solicitar(
    `/buscar${consulta({ q, ronda: rondaId, proyecto })}`,
    { signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]) },
));

export const fetchRondas = (proyecto) => solicitar(`/rondas${consulta({ proyecto })}`);
export const crearRonda = (datos) => solicitar('/rondas', { method: 'POST', json: datos });
export const actualizarRonda = ({ id, ...cambios }) => solicitar(`/rondas/${id}`, { method: 'PATCH', json: cambios });
export const borrarRonda = (id) => solicitar(`/rondas/${id}`, { method: 'DELETE' });
export const fetchUsuarios = () => solicitar('/rondas/usuarios');
export const fetchAsignaciones = (rondaId) => solicitar(`/rondas/${rondaId}/asignaciones`);
export const guardarAsignaciones = ({ rondaId, items }) => solicitar(
    `/rondas/${rondaId}/asignaciones`,
    { method: 'PUT', json: items },
);

export const fetchMisCasos = (rondaId) => solicitar(`/mis-casos${consulta({ ronda: rondaId })}`);
export const guardarResultado = ({ casoId, ...datos }) => solicitar(
    `/resultados/${encodeURIComponent(casoId)}`,
    { method: 'PUT', json: datos },
);

export const reportarFalla = (form) => solicitar('/fallas', { method: 'POST', form });
export const fetchFallas = (filtros) => solicitar(`/fallas${consulta(filtros)}`);
export const urlInformeFallas = (filtros) => `/api/fallas/informe.csv${consulta(filtros)}`;
export const actualizarFalla = ({ id, ...cambios }) => solicitar(`/fallas/${id}`, { method: 'PATCH', json: cambios });
export const actualizarComentario = ({ id, ...cambios }) => solicitar(`/comentarios/${id}`, { method: 'PATCH', json: cambios });
const RUTAS_SEGUIMIENTO = { falla: 'fallas', comentario: 'comentarios' };
export const responder = (objeto, { id, texto }) => solicitar(`/${RUTAS_SEGUIMIENTO[objeto]}/${id}/respuestas`, { method: 'POST', json: { texto } });

export const fetchTablero = (rondaId, audiencia = 'todas') => solicitar(`/tablero${consulta({ ronda: rondaId, audiencia })}`);

export const fetchHerramientas = (rondaId) => solicitar(`/herramientas${consulta({ ronda: rondaId })}`);
export const decidirHerramienta = ({ herramientaId, ...datos }) => solicitar(
    `/decisiones/${encodeURIComponent(herramientaId)}`,
    { method: 'PUT', json: datos },
);

export const fetchComentarios = (rondaId, proyecto) => solicitar(`/comentarios${consulta({ ronda: rondaId, proyecto })}`);
export const fetchAccesos = () => solicitar('/accesos');
export const guardarAccesos = (items) => solicitar('/accesos', { method: 'PUT', json: items });
export const fetchComentariosCaso = (casoId, rondaId) => solicitar(
    `/comentarios/caso/${encodeURIComponent(casoId)}${consulta({ ronda: rondaId })}`,
);
export const fetchCuentasPrueba = (rondaId) => solicitar(`/cuentas-prueba${consulta({ ronda: rondaId })}`);
export const fetchAprobaciones = (rondaId) => solicitar(`/aprobaciones${consulta({ ronda: rondaId })}`);
export const registrarAprobaciones = (datos) => solicitar('/aprobaciones', { method: 'POST', json: datos });

export const fetchAvisos = async () => avisosSchema.parse(await solicitar('/avisos'));
export const fetchAvisosNoLeidos = async () => noLeidosSchema.parse(await solicitar('/avisos/no-leidos'));
export const fetchPersonasAviso = async () => personasAvisoSchema.parse(await solicitar('/avisos/personas'));
export const marcarAvisoLeido = async (id) => avisoSchema.parse(await solicitar(`/avisos/${id}/leido`, { method: 'POST' }));
export const marcarAvisosLeidos = async () => noLeidosSchema.parse(await solicitar('/avisos/leidos', { method: 'POST' }));
export const crearAviso = async (datos) => avisosSchema.parse(await solicitar('/avisos', { method: 'POST', json: datos }));

export const registrarPresencia = (datos) => solicitar('/presencia', { method: 'POST', json: datos });
export const fetchPresencia = async (proyecto) => presenciasSchema.parse(await solicitar(`/presencia${consulta({ proyecto })}`));
export const fetchResumenActividad = async (proyecto) => resumenActividadSchema.parse(await solicitar(`/actividad/resumen${consulta({ proyecto })}`));
export const fetchActividad = async (filtros) => actividadSchema.parse(await solicitar(`/actividad${consulta(filtros)}`));
