module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    // react-native-reanimated 4 delega la transformación de "worklets" en este plugin;
    // debe ir el último de la lista (requisito de Reanimated/Worklets).
    plugins: ['react-native-worklets/plugin'],
  };
};
