const HOST = process.env.REACT_APP_SERVER_HOST
const PORT = process.env.REACT_APP_SERVER_PORT
const HOST_DATABASE = process.env.REACT_APP_SERVER_DATABASE_HOST

export const BASE_URL = `http://${HOST}:${PORT}`
export const WS_BASE_URL = `ws://${HOST}:${PORT}`
export const DATABASE_URL_HOST = `${HOST_DATABASE}`
