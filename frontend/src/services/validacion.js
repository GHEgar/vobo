import { consulta, solicitar } from '@/services/api';
import {
    avisoSchema,
    avisosSchema,
    contenidoSchema,
    instanciaSchema,
    noLeidosSchema,
    personasAvisoSchema,
    sesionSchema,
} from '@/services/esquemas';

export const fetchInstancia = async () => instanciaSchema.parse(await solicitar('/instancia'));
export const fetchModo = () => solicitar('/auth/modo');
export const fetchSesion = async () => sesionSchema.parse(await solicitar('/auth/me'));
export const fetchUsuariosLocales = () => solicitar('/auth/usuarios-locales');
export const entrarLocal = (clave) => solicitar('/auth/local', { method: 'POST', json: { clave } });
export const salir = () => solicitar('/auth/logout', { method: 'POST' });

export const fetchContenido = async () => contenidoSchema.parse(await solicitar('/contenido'));

export const fetchRondas = () => solicitar('/rondas');
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
export const actualizarFalla = ({ id, ...cambios }) => solicitar(`/fallas/${id}`, { method: 'PATCH', json: cambios });

export const fetchTablero = (rondaId, audiencia = 'todas') => solicitar(`/tablero${consulta({ ronda: rondaId, audiencia })}`);

export const fetchHerramientas = (rondaId) => solicitar(`/herramientas${consulta({ ronda: rondaId })}`);
export const decidirHerramienta = ({ herramientaId, ...datos }) => solicitar(
    `/decisiones/${encodeURIComponent(herramientaId)}`,
    { method: 'PUT', json: datos },
);

export const fetchComentarios = (rondaId) => solicitar(`/comentarios${consulta({ ronda: rondaId })}`);
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
