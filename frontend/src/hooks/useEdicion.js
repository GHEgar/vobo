import { use } from 'react';
import { EdicionContext } from '@/contexts/EdicionContext';

const SIN_EDICION = { disponible: false, activo: false, sistemas: [], fijar: () => {}, alternar: () => {} };

export const useEdicion = () => use(EdicionContext) ?? SIN_EDICION;
