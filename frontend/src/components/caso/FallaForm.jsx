import { useState } from 'react';
import { Button } from '@/components/Button';
import { Dragger } from '@/components/Dragger';
import { RadioGroup } from '@/components/RadioGroup';
import { TextField } from '@/components/Field';
import { useReportarFalla } from '@/hooks/useValidacion';
import { REPRODUCIBLE, opciones } from '@/utils/etiquetas';
import { describirNavegador, formatearFecha } from '@/utils/formato';

const Dato = ({ termino, children }) => (
    <div className="flex flex-col">
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="tipo-media text-sm text-texto">{children}</dd>
    </div>
);

const TIPOS = [
    { valor: 'falla', texto: 'Falló' },
    { valor: 'no_pude', texto: 'No pude probarlo' },
];

const SelectorTipo = ({ valor, onCambiar }) => (
    <div role="radiogroup" aria-label="Qué pasó en este paso" className="flex w-fit gap-1 rounded-full bg-fondo p-1">
        {TIPOS.map((t) => {
            const activo = valor === t.valor;
            return (
                <button
                    key={t.valor}
                    type="button"
                    role="radio"
                    aria-checked={activo}
                    onClick={() => onCambiar(t.valor)}
                    className={`h-[34px] rounded-full px-5 tipo-negrita text-sm ${activo ? 'bg-falla text-white' : 'bg-transparent text-texto-tenue hover:text-falla'}`}
                >
                    {t.texto}
                </button>
            );
        })}
    </div>
);

export const FallaForm = ({ caso, ronda, usuario, paso, onCancelar, onEnviada }) => {
    const reportar = useReportarFalla();
    const fuera = paso === null;
    const [tipo, setTipo] = useState('falla');
    const noPude = tipo === 'no_pude';
    const [obtenido, setObtenido] = useState('');
    const [reproducible, setReproducible] = useState('');
    const [url, setUrl] = useState('');
    const [version, setVersion] = useState('');
    const [imagenes, setImagenes] = useState([]);
    const [errores, setErrores] = useState({});
    const [ahora] = useState(() => new Date().toISOString());

    const enviar = async (e) => {
        e.preventDefault();
        const nuevos = {};
        if (obtenido.trim().length < 3) nuevos.obtenido = noPude ? 'Explica qué te impidió probarlo' : 'Describe qué viste en pantalla';
        if (!noPude && !reproducible) nuevos.reproducible = 'Elige una opción';
        setErrores(nuevos);
        if (Object.keys(nuevos).length) return;
        const form = new FormData();
        form.append('ronda_id', ronda.id);
        form.append('caso_id', caso.id);
        form.append('obtenido', obtenido.trim());
        form.append('tipo', tipo);
        if (!noPude) form.append('reproducible', reproducible);
        if (!fuera) form.append('paso', paso);
        form.append('navegador', navigator.userAgent);
        form.append('url', url.trim());
        form.append('version_visible', version.trim());
        imagenes.forEach((imagen) => form.append('imagenes', imagen));
        try {
            await reportar.mutateAsync(form);
        } catch {
            return;
        }
        onEnviada(tipo);
    };

    return (
        <form onSubmit={enviar} noValidate className="flex flex-col">
            <h2 className="tipo-negrita text-lg text-falla">{fuera ? 'Reportar algo fuera de los pasos' : `Reportar el paso ${paso + 1}`}</h2>
            {!fuera && (
                <div className="mt-3">
                    <SelectorTipo valor={tipo} onCambiar={setTipo} />
                </div>
            )}
            <dl className="mt-3 grid grid-cols-1 gap-3 rounded-2xl bg-fondo p-4 sm:grid-cols-2 lg:grid-cols-3">
                <Dato termino="Caso">{caso.id} · {caso.titulo}</Dato>
                <Dato termino="Paso">{fuera ? 'Fuera de los pasos' : `${paso + 1}. ${caso.pasos[paso].texto}`}</Dato>
                <Dato termino="Ronda">{ronda.nombre}</Dato>
                <Dato termino="Quién reporta">{usuario.nombre}</Dato>
                <Dato termino="Navegador">{describirNavegador()}</Dato>
                <Dato termino="Fecha">{formatearFecha(ahora)}</Dato>
                <Dato termino="Severidad">{caso.severidad}</Dato>
            </dl>
            <TextField
                id="obtenido"
                label={fuera ? '¿Qué encontraste?' : noPude ? '¿Por qué no pudiste probarlo?' : '¿Qué pasó en su lugar?'}
                tooltip={fuera ? 'Un error, un texto raro o algo que falta y que ningún paso pide revisar.' : noPude ? 'Por ejemplo: no tenías la cuenta, el entorno no cargaba o faltaba algo que pide «Antes de empezar».' : `Lo que debía pasar: ${caso.esperado}`}
                placeholder={fuera ? 'Describe qué viste y dónde, con el texto exacto de los mensajes si los hubo' : noPude ? 'Qué te faltó o qué te impidió hacer el paso' : 'Describe lo que viste en pantalla, con el texto exacto de los mensajes si los hubo'}
                multiline
                required
                value={obtenido}
                onChange={(e) => setObtenido(e.target.value)}
                error={errores.obtenido}
            />
            {!noPude && <RadioGroup
                name="reproducible"
                label="¿Se repite?"
                tooltip="Intenta los pasos una vez más antes de responder."
                options={opciones(REPRODUCIBLE)}
                value={reproducible}
                onChange={setReproducible}
                required
                error={errores.reproducible}
            />}
            <div className="grid grid-cols-1 gap-x-6 md:grid-cols-2">
                <TextField id="url" label="Dirección donde pasó" tooltip="Copia la dirección de la barra del navegador." placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
                <TextField id="version" label="Versión que se ve" tooltip="Si el sistema muestra un número de versión, normalmente al pie de página o en el menú, cópialo aquí." placeholder="Por ejemplo 2.3.0" value={version} onChange={(e) => setVersion(e.target.value)} />
            </div>
            <Dragger label="Capturas de pantalla" tooltip="Con Windows + Mayús + S recortas una parte de la pantalla; luego pégala en Paint y guárdala." archivos={imagenes} onChange={setImagenes} />
            {reportar.error && <p className="mt-3 tipo-media text-sm text-error-fuerte">{reportar.error.message}</p>}
            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <Button label="Cancelar" variant="secondary" onClick={onCancelar} />
                <Button label={noPude ? 'Enviar' : 'Enviar falla'} variant="danger" type="submit" loading={reportar.isPending} />
            </div>
        </form>
    );
};
