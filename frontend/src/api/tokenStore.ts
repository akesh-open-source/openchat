export interface TokenStore {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  setTokens(tokens: { access_token: string; refresh_token: string }): void;
  clear(): void;
}

export class MemoryTokenStore implements TokenStore {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  setTokens(tokens: { access_token: string; refresh_token: string }): void {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
  }

  clear(): void {
    this.accessToken = null;
    this.refreshToken = null;
  }
}

const ACCESS_KEY = "openchat.access_token";
const REFRESH_KEY = "openchat.refresh_token";

export class LocalStorageTokenStore implements TokenStore {
  getAccessToken(): string | null {
    return window.localStorage.getItem(ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return window.localStorage.getItem(REFRESH_KEY);
  }

  setTokens(tokens: { access_token: string; refresh_token: string }): void {
    window.localStorage.setItem(ACCESS_KEY, tokens.access_token);
    window.localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  }

  clear(): void {
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  }
}
