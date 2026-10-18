import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/admin';
import { recargarEstilos } from '@/utils/estilos';

const ROLES = ['admin', 'roles'];
const PERSONAS = ['admin', 'personas'];
const INVITACIONES = ['admin', 'invitaciones'];

const useMutacion = (mutationFn, claves = []) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn,
        onSuccess: () => claves.forEach((queryKey) => queryClient.invalidateQueries({ queryKey })),
    });
};

export const usePermisosCatalogo = () => useQuery({ queryKey: ['admin', 'permisos'], queryFn: api.fetchPermisos, staleTime: Infinity });
export const useRoles = () => useQuery({ queryKey: ROLES, queryFn: api.fetchRoles });
export const usePersonas = () => useQuery({ queryKey: PERSONAS, queryFn: api.fetchPersonas });
export const useInvitaciones = () => useQuery({ queryKey: INVITACIONES, queryFn: api.fetchInvitaciones });

export const useCrearRol = () => useMutacion(api.crearRol, [ROLES]);
export const useActualizarRol = () => useMutacion(api.actualizarRol, [ROLES]);
export const useBorrarRol = () => useMutacion(api.borrarRol, [ROLES, PERSONAS]);
export const useAsignarRoles = () => useMutacion(api.asignarRoles, [PERSONAS, ['sesion']]);
export const useFijarCuentaActiva = () => useMutacion(api.fijarCuentaActiva, [PERSONAS]);
export const useCrearRestablecimiento = () => useMutacion(api.crearRestablecimiento);
export const useInvitar = () => useMutacion(api.invitar, [INVITACIONES]);
export const useRevocarInvitacion = () => useMutacion(api.revocarInvitacion, [INVITACIONES]);

const CONFIGURACION = ['admin', 'configuracion'];
export const CLAVE_MUTACION = ['configuracion'];

const useMutacionConfiguracion = (mutationFn) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: CLAVE_MUTACION,
        mutationFn,
        onSuccess: (estado) => {
            queryClient.setQueryData(CONFIGURACION, estado);
            queryClient.invalidateQueries({ queryKey: ['instancia'] });
            recargarEstilos();
        },
    });
};

export const useConfiguracion = () => useQuery({ queryKey: CONFIGURACION, queryFn: api.fetchConfiguracion });
export const useGuardarConfiguracion = () => useMutacionConfiguracion(api.guardarConfiguracion);
export const useRestablecerConfiguracion = () => useMutacionConfiguracion(api.restablecerConfiguracion);
export const useSubirMarca = () => useMutacionConfiguracion(api.subirMarca);
export const useQuitarMarca = () => useMutacionConfiguracion(api.quitarMarca);

const PROYECTOS = ['admin', 'proyectos'];
const CON_PROYECTOS = [PROYECTOS, ['proyectos'], ['instancia'], ['rondas']];

export const useProyectosAdmin = () => useQuery({ queryKey: PROYECTOS, queryFn: api.fetchProyectosAdmin });
export const useCrearProyecto = () => useMutacion(api.crearProyecto, CON_PROYECTOS);
export const useActualizarProyecto = () => useMutacion(api.actualizarProyecto, CON_PROYECTOS);
export const useOrdenarProyectos = () => useMutacion(api.ordenarProyectos, CON_PROYECTOS);
export const useBorrarProyecto = () => useMutacion(api.borrarProyecto, CON_PROYECTOS);

const PANTALLAS = ['admin', 'pantallas'];

export const usePantallas = () => useQuery({ queryKey: PANTALLAS, queryFn: api.fetchPantallas });
export const useCrearPantalla = () => useMutacion(api.crearPantalla, [PANTALLAS]);
export const useActualizarPantalla = () => useMutacion(api.actualizarPantalla, [PANTALLAS]);
export const useRegenerarPantalla = () => useMutacion(api.regenerarPantalla, [PANTALLAS]);
export const useBorrarPantalla = () => useMutacion(api.borrarPantalla, [PANTALLAS]);
