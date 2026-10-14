export const IconoTooltip = ({ className = '' }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" aria-hidden="true" focusable="false" className={className}>
        <circle cx="10" cy="10" r="10" fill="var(--color-aviso-fondo)" />
        <path
            d="M2.167-7.474v.407H4.09v-.209c0-.352.231-.6.747-.835a1.87,1.87,0,0,0,1.242-1.78c0-1.363-1.11-2.264-2.8-2.264S.5-11.232.442-9.726H2.376a.748.748,0,0,1,.857-.791c.516,0,.813.22.813.615,0,.33-.2.549-.725.758A1.53,1.53,0,0,0,2.167-7.474ZM1.958-5.3A1.123,1.123,0,0,0,3.134-4.155,1.123,1.123,0,0,0,4.31-5.3,1.123,1.123,0,0,0,3.134-6.441,1.123,1.123,0,0,0,1.958-5.3Z"
            transform="translate(6.65 17.879)"
            fill="var(--color-aviso)"
        />
    </svg>
);

export const IconoCerrar = ({ className = '' }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 41 41" aria-hidden="true" focusable="false" className={className}>
        <circle cx="20.5" cy="20.5" r="20.5" fill="var(--color-fondo)" />
        <path
            d="M8.266,6.6l6.25-6.25a1.181,1.181,0,0,1,1.67,1.67l-6.25,6.25,6.25,6.25a1.181,1.181,0,0,1-1.67,1.67l-6.25-6.25-6.25,6.25a1.181,1.181,0,0,1-1.67-1.67L6.6,8.266.346,2.016A1.181,1.181,0,1,1,2.016.346Z"
            transform="translate(11.622 11.622)"
            fill="var(--color-neutro-icono)"
        />
    </svg>
);

const TRAZO = { fill: 'var(--color-primario)', stroke: 'var(--color-primario)', strokeWidth: 1 };

export const IconoSubir = ({ className = '' }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 94 94" aria-hidden="true" focusable="false" className={className}>
        <circle cx="47" cy="47" r="47" fill="var(--color-primario-suave)" />
        <g transform="translate(22.452 20.088)">
            <path
                {...TRAZO}
                d="M34.2,10.587,27.191,2.081A5.572,5.572,0,0,0,22.9,0H5.736A5.544,5.544,0,0,0,1.684,1.819,6.469,6.469,0,0,0,0,6.195V32.3a6.47,6.47,0,0,0,1.684,4.376A5.546,5.546,0,0,0,5.736,38.5H29.91a5.545,5.545,0,0,0,4.052-1.819A6.471,6.471,0,0,0,35.646,32.3V14.713A6.529,6.529,0,0,0,34.2,10.587ZM33.83,32.3h0A4.42,4.42,0,0,1,32.683,35.3a3.786,3.786,0,0,1-2.773,1.24H5.737A4.088,4.088,0,0,1,1.815,32.3V6.2A4.088,4.088,0,0,1,5.737,1.961H22.9a3.778,3.778,0,0,1,2.929,1.419l7.007,8.506a4.425,4.425,0,0,1,.992,2.827Z"
                transform="translate(6.726 7.263)"
            />
            <path
                {...TRAZO}
                d="M36.483,30.312a.853.853,0,0,0-1.114,0l-4.834,4.175h0a.977.977,0,0,0-.382.658,1.023,1.023,0,0,0,.192.75.9.9,0,0,0,.606.363.854.854,0,0,0,.664-.208l3.341-2.912V45.458a.9.9,0,1,0,1.8,0V33.141L40.1,36.052l0,0a.854.854,0,0,0,.664.208.894.894,0,0,0,.6-.364,1.012,1.012,0,0,0,.2-.716.983.983,0,0,0-.335-.656Z"
                transform="translate(-11.329 -9.804)"
            />
            <path
                {...TRAZO}
                d="M31.132,23.076H40.8a.941.941,0,0,0,.9-.974.951.951,0,0,0-.9-.986H31.132a.951.951,0,0,0-.9.986.941.941,0,0,0,.9.974"
                transform="translate(-11.382 -4.707)"
            />
        </g>
    </svg>
);

export const IconoCampana = ({ className = '' }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false" className={className}>
        <path
            d="M12 3a6 6 0 0 0-6 6v3.6l-1.6 2.7A1 1 0 0 0 5.3 17h13.4a1 1 0 0 0 .9-1.7L18 12.6V9a6 6 0 0 0-6-6Z"
            fill="none"
            stroke="var(--color-primario)"
            strokeWidth="1.8"
            strokeLinejoin="round"
        />
        <path d="M9.5 19a2.5 2.5 0 0 0 5 0" fill="none" stroke="var(--color-primario)" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
);
