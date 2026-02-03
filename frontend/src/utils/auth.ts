const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export const setToken = (token: string, username?: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
  if (username) {
    localStorage.setItem(USER_KEY, username);
  }
};

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getUser = (): string | null => {
  return localStorage.getItem(USER_KEY);
};

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};
