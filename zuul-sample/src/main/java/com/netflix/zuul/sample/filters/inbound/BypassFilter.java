/*
 * Copyright 2018 Netflix, Inc.
 *
 *      Licensed under the Apache License, Version 2.0 (the "License");
 *      you may not use this file except in compliance with the License.
 *      You may obtain a copy of the License at
 *
 *          http://www.apache.org/licenses/LICENSE-2.0
 *
 *      Unless required by applicable law or agreed to in writing, software
 *      distributed under the License is distributed on an "AS IS" BASIS,
 *      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *      See the License for the specific language governing permissions and
 *      limitations under the License.
 */

package com.netflix.zuul.sample.filters.inbound;

import com.netflix.zuul.filters.http.HttpInboundSyncFilter;
import com.netflix.zuul.message.http.HttpRequestMessage;
import com.netflix.zuul.message.http.HttpResponseMessage;
import com.netflix.zuul.message.http.HttpResponseMessageImpl;
import io.netty.handler.codec.http.HttpResponseStatus;

/**
 * Vulnerable filter that performs a weak path check.
 * It blocks any path starting with /admin using the raw path, which is susceptible to normalization bypass.
 */
public class BypassFilter extends HttpInboundSyncFilter {

    @Override
    public int filterOrder() {
        return 20; // After Routes (0)
    }

    @Override
    public boolean shouldFilter(HttpRequestMessage request) {
        return true;
    }

    @Override
    public HttpRequestMessage apply(HttpRequestMessage request) {
        String path = request.getPath();

        // Weak path check: only blocks if it starts with /admin in the RAW path
        // Vulnerable to: /public/%2e%2e/admin/secrets
        if (path.startsWith("/admin")) {
            // Block access with 403 Forbidden
            HttpResponseMessage response = new HttpResponseMessageImpl(request.getContext(), request, HttpResponseStatus.FORBIDDEN.code());
            response.setBodyAsText("Access Denied by BypassFilter");

            request.getContext().stopFilterProcessing();
            request.getContext().setStaticResponse(response);
        }

        return request;
    }
}
