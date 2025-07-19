
const { default: makeWASocket, DisconnectReason, useSingleFileAuthState } = require('@adiwajshing/baileys');
const { Boom } = require('@hapi/boom');
const axios = require('axios');

async function connectToWhatsApp() {
    const { state, saveState } = useSingleFileAuthState('./auth_info_baileys.json');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error instanceof Boom) && lastDisconnect.error.output.statusCode !== DisconnectReason.loggedOut;
            console.log('connection closed due to ', lastDisconnect.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('opened connection');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        console.log(JSON.stringify(m, undefined, 2));

        const msg = m.messages[0];
        if (!msg.key.fromMe && m.type === 'notify') {
            const message = msg.message.conversation || msg.message.extendedTextMessage.text;
            const from = msg.key.remoteJid;

            // Enviar el mensaje al orquestador
            try {
                const response = await axios.post('http://localhost:5000/derek', {
                    input: message,
                    user_id: from // Usar el número de teléfono como user_id
                });

                await sock.sendMessage(from, { text: response.data });
            } catch (error) {
                console.error('Error sending message to orchestrator:', error);
            }
        }
    });

    sock.ev.on('creds.update', saveState);
}

connectToWhatsApp();
