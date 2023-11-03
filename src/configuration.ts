import 'dotenv/config';

export default (isTests = false) => {
  const {
    MONGO_URI,
    SERVER_DOMAIN,
    TELEGRAM_BOT_TOKEN,
    API_VERSION,

  } = process.env;
  if (!MONGO_URI) {
    console.log('Environment Var: MONGO_URI is required!');
    process.exit(1);
  }

  if (!TELEGRAM_BOT_TOKEN) {
    console.log('Environment Var: TELEGRAM_BOT_TOKEN is required!');
    process.exit(1);
  }
  if (!SERVER_DOMAIN) {
    console.log('Environment Var: SERVER_DOMAIN is required');
    process.exit(1);
  } else if (SERVER_DOMAIN.endsWith('/')) {
    console.log(
      'Please make sure that the SERVER_DOMAIN is formatted correctly. It should follow the standard https://parasum.com or http://localhost:3000',
    );
    process.exit(1);
  }



  if (!API_VERSION) {
    console.log('Environment Var: API_VERSION is required!');
    process.exit(1);
  }
  return {
    mongoUri: MONGO_URI.trim(),
    serverDomain: SERVER_DOMAIN.trim(),
    apiVersion: +API_VERSION.trim() || 1,
    telegramBotToken: TELEGRAM_BOT_TOKEN,

  };
};
