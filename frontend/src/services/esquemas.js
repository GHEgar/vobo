import { z } from 'zod';

const paso = z.object({ texto: z.string(), procedimiento: z.string().nullish() });

const caso = z.object({
    id: z.string(),
    familia: z.enum(['A', 'B', 'C', 'D', 'E', 'T']),
    herramienta: z.string().default('general'),
    titulo: z.string(),
    rol: z.string().default(''),
    cuenta: z.string().default(''),
    modo: z.enum(['prod', 'beta', 'dev']),
    antes: z.string().default(''),
    pasos: z.array(paso),
    esperado: z.string(),
    severidad: z.enum(['critica', 'alta', 'media', 'baja']),
});

const seccion = z.object({
    id: z.string(),
    orden: z.number(),
    titulo: z.string(),
    sistema: z.string(),
    audiencia: z.enum(['funcional', 'tecnica']).default('funcional'),
    resumen: z.string(),
    que_cambia: z.array(z.string()),
    donde: z.string(),
    herramientas: z.array(z.object({
        id: z.string(),
        nombre: z.string(),
        hoy: z.enum(['prod', 'beta', 'oculto']),
    })),
    media: z.array(z.object({ procedimiento: z.string(), pie: z.string(), url: z.string().nullish() })),
    casos: z.array(caso),
});

export const contenidoSchema = z.object({
    secciones: z.array(seccion),
    procedimientos: z.array(z.looseObject({
        id: z.string(),
        titulo: z.string(),
        descripcion: z.string(),
        url: z.string().nullish(),
    })),
    errores: z.array(z.string()).default([]),
});

export const sesionSchema = z.object({
    csrf_token: z.string(),
    usuario: z.object({
        email: z.string(),
        nombre: z.string(),
        permisos: z.array(z.string()),
        paginas: z.array(z.string()).default([]),
        origen: z.string().default('oidc'),
        tiene_cuenta: z.boolean().default(false),
        debe_cambiar: z.boolean().default(false),
    }),
});

const sistemaSchema = z.object({ clave: z.string(), nombre: z.string() });

const proyectoPublicoSchema = z.object({
    clave: z.string(),
    nombre: z.string(),
    color_nombre: z.string().nullable().default(null),
    por_omision: z.boolean().default(false),
});

export const instanciaSchema = z.object({
    producto: z.string().default(''),
    nombre: z.string().default(''),
    descripcion: z.string().default(''),
    logo: z.object({ claro: z.string(), oscuro: z.string(), alt: z.string() }).nullable().default(null),
    favicon: z.string().default(''),
    color_tema: z.string().default(''),
    entrada: z.object({ titulo: z.string().default(''), mensaje: z.string().default('') }).default({ titulo: '', mensaje: '' }),
    proyectos: z.array(sistemaSchema).default([]),
    sistemas: z.array(sistemaSchema).optional(),
    proyecto: proyectoPublicoSchema.nullable().default(null),
}).transform(({ sistemas, ...resto }) => ({ ...resto, sistemas: sistemas ?? resto.proyectos }));

export const proyectoSchema = z.object({
    id: z.number(),
    clave: z.string(),
    nombre: z.string(),
    descripcion: z.string().default(''),
    color_nombre: z.string().nullable().default(null),
    orden: z.number().default(0),
    archivado: z.boolean().default(false),
    por_omision: z.boolean().default(false),
});

export const proyectosSchema = z.array(proyectoSchema);

export const avisoSchema = z.object({
    id: z.number(),
    usuario_email: z.string(),
    titulo: z.string(),
    mensaje: z.string(),
    falla_id: z.number().nullable(),
    caso_id: z.string().nullable(),
    proyecto_clave: z.string().nullable().default(null),
    autor_email: z.string(),
    autor_nombre: z.string(),
    creado: z.string(),
    leido: z.string().nullable(),
});

export const avisosSchema = z.array(avisoSchema);

export const noLeidosSchema = z.object({ total: z.number() });

export const personasAvisoSchema = z.array(z.object({ email: z.string(), nombre: z.string() }));

export const resultadosBusquedaSchema = z.array(z.object({
    tipo: z.enum(['seccion', 'caso', 'paso', 'herramienta', 'procedimiento']),
    id: z.string(),
    titulo: z.string(),
    contexto: z.string(),
    ruta: z.string(),
}));

export const presenciasSchema = z.array(z.object({
    email: z.string(),
    nombre: z.string(),
    ruta: z.string(),
    caso_id: z.string().nullable(),
    caso_titulo: z.string(),
    paso: z.number().nullable(),
    pasos_total: z.number().nullable(),
    seccion_id: z.string().nullable(),
    seccion_titulo: z.string(),
    accion: z.string(),
    ronda_id: z.number().nullable(),
    estado: z.enum(['activo', 'inactivo']),
    hace_segundos: z.number(),
    yo: z.boolean(),
}));
