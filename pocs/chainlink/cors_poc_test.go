package network_test

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestHTTPServer_CORS_Bypass_PoC(t *testing.T) {
	// Allowed origin with wildcard
	allowedOrigins := []string{"https://*.ethereum.org"}
	_, handler, url := startNewServer(t, 100_000, 100_000, true, allowedOrigins)

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200).Maybe()

	// Malicious origin that ends with "ethereum.org" but is not a subdomain
	// The current logic is:
	// if strings.HasPrefix(allowedHost, "*.") {
	//     allowedHost = allowedHost[2:]
	//     if strings.HasSuffix(originHost, allowedHost) { return true }
	// }
	// So "attackerethereum.org" has suffix "ethereum.org" -> TRUE
	origin := "https://attackerethereum.org"
	resp := sendRequest(t, url, []byte("test"), http.MethodPost, &origin)

	// Verification
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"), "VULNERABILITY: CORS bypass successful! Attacker origin was accepted.")
}
