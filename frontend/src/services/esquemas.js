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
    }),
});

export const instanciaSchema = z.object({
    nombre: z.string().default(''),
    descripcion: z.string().default(''),
    proyectos: z.array(z.object({ clave: z.string(), nombre: z.string() })).default([]),
});

export const avisoSchema = z.object({
    id: z.number(),
    usuario_email: z.string(),
    titulo: z.string(),
    mensaje: z.string(),
    falla_id: z.number().nullable(),
    caso_id: z.string().nullable(),
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
