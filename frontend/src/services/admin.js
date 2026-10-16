import { solicitar } from '@/services/api';

export const fetchPermisos = () => solicitar('/admin/permisos');
export const fetchRoles = () => solicitar('/admin/roles');
export const crearRol = (datos) => solicitar('/admin/roles', { method: 'POST', json: datos });
export const actualizarRol = ({ id, ...cambios }) => solicitar(`/admin/roles/${id}`, { method: 'PATCH', json: cambios });
export const borrarRol = (id) => solicitar(`/admin/roles/${id}`, { method: 'DELETE' });

export const fetchPersonas = () => solicitar('/admin/personas');
export const asignarRoles = ({ id, roles }) => solicitar(`/admin/personas/${id}/roles`, { method: 'PUT', json: { roles } });
export const fijarCuentaActiva = ({ id, activa }) => solicitar(`/admin/personas/${id}/cuenta`, { method: 'PATCH', json: { activa } });
export const crearRestablecimiento = (id) => solicitar(`/admin/personas/${id}/restablecer`, { method: 'POST' });

export const fetchInvitaciones = () => solicitar('/admin/invitaciones');
export const invitar = (datos) => solicitar('/admin/invitaciones', { method: 'POST', json: datos });
export const revocarInvitacion = (id) => solicitar(`/admin/invitaciones/${id}`, { method: 'DELETE' });

const CONFIGURACION = '/admin/configuracion';

const conArchivo = (archivo) => {
    const form = new FormData();
    form.append('archivo', archivo);
    return form;
};

export const fetchConfiguracion = () => solicitar(CONFIGURACION);
export const guardarConfiguracion = (cambios) => solicitar(CONFIGURACION, { method: 'PUT', json: cambios });
export const restablecerConfiguracion = (clave) => solicitar(`${CONFIGURACION}/${clave}`, { method: 'DELETE' });
export const subirMarca = ({ ranura, archivo }) => solicitar(`${CONFIGURACION}/marca/${ranura}`, { method: 'PUT', form: conArchivo(archivo) });
export const quitarMarca = (ranura) => solicitar(`${CONFIGURACION}/marca/${ranura}`, { method: 'DELETE' });

const PROYECTOS = '/admin/proyectos';

export const fetchProyectosAdmin = () => solicitar(PROYECTOS);
export const crearProyecto = (datos) => solicitar(PROYECTOS, { method: 'POST', json: datos });
export const actualizarProyecto = ({ id, ...cambios }) => solicitar(`${PROYECTOS}/${id}`, { method: 'PATCH', json: cambios });
export const ordenarProyectos = (ids) => solicitar(`${PROYECTOS}/orden`, { method: 'PUT', json: { ids } });
export const borrarProyecto = (id) => solicitar(`${PROYECTOS}/${id}`, { method: 'DELETE' });
