import { solicitar } from '@/services/api';

const base = (token) => `/pantalla/${encodeURIComponent(token)}`;

export const fetchPantalla = (token) => solicitar(base(token));
export const fetchDatosPantalla = (token) => solicitar(`${base(token)}/datos`);
