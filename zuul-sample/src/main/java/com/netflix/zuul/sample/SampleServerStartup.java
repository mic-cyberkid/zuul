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

package com.netflix.zuul.sample;

import com.netflix.appinfo.ApplicationInfoManager;
import com.netflix.config.DynamicIntProperty;
import com.netflix.discovery.EurekaClient;
import com.netflix.netty.common.accesslog.AccessLogPublisher;
import com.netflix.netty.common.channel.config.ChannelConfig;
import com.netflix.netty.common.channel.config.CommonChannelConfigKeys;
import com.netflix.netty.common.metrics.EventLoopGroupMetrics;
import com.netflix.netty.common.proxyprotocol.StripUntrustedProxyHeadersHandler;
import com.netflix.netty.common.status.ServerStatusManager;
import com.netflix.spectator.api.Registry;
import com.netflix.zuul.FilterLoader;
import com.netflix.zuul.FilterUsageNotifier;
import com.netflix.zuul.RequestCompleteHandler;
import com.netflix.zuul.context.SessionContextDecorator;
import com.netflix.zuul.netty.server.BaseServerStartup;
import com.netflix.zuul.netty.server.DefaultEventLoopConfig;
import com.netflix.zuul.netty.server.DirectMemoryMonitor;
import com.netflix.zuul.netty.server.NamedSocketAddress;
import com.netflix.zuul.netty.server.SocketAddressProperty;
import com.netflix.zuul.netty.server.ZuulDependencyKeys;
import com.netflix.zuul.netty.server.ZuulServerChannelInitializer;
import com.netflix.zuul.netty.server.push.PushConnectionRegistry;
import com.netflix.zuul.sample.push.SamplePushMessageSenderInitializer;
import com.netflix.zuul.sample.push.SampleWebSocketPushChannelInitializer;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.group.ChannelGroup;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/**
 * Sample Server Startup - class that configures the Netty server startup settings
 * <p>
 * Author: Arthur Gonigberg
 * Date: November 20, 2017
 */
public class SampleServerStartup extends BaseServerStartup {

    private final PushConnectionRegistry pushConnectionRegistry;

    public SampleServerStartup(
            ServerStatusManager serverStatusManager,
            FilterLoader filterLoader,
            SessionContextDecorator sessionCtxDecorator,
            FilterUsageNotifier usageNotifier,
            RequestCompleteHandler reqCompleteHandler,
            Registry registry,
            DirectMemoryMonitor directMemoryMonitor,
            EventLoopGroupMetrics eventLoopGroupMetrics,
            EurekaClient discoveryClient,
            ApplicationInfoManager applicationInfoManager,
            AccessLogPublisher accessLogPublisher,
            PushConnectionRegistry pushConnectionRegistry,
            SamplePushMessageSenderInitializer pushSenderInitializer) {
        super(
                serverStatusManager,
                filterLoader,
                sessionCtxDecorator,
                usageNotifier,
                reqCompleteHandler,
                registry,
                directMemoryMonitor,
                eventLoopGroupMetrics,
                new DefaultEventLoopConfig(),
                discoveryClient,
                applicationInfoManager,
                accessLogPublisher);
        this.pushConnectionRegistry = pushConnectionRegistry;
    }

    @Override
    protected Map<NamedSocketAddress, ChannelInitializer<?>> chooseAddrsAndChannels(ChannelGroup clientChannels) {
        Map<NamedSocketAddress, ChannelInitializer<?>> addrsToChannels = new HashMap<>();

        // Regular HTTP proxy on port 7001
        SocketAddress sockAddr;
        String metricId;
        {
            int port = new DynamicIntProperty("zuul.server.port.main", 7001).get();
            sockAddr = new SocketAddressProperty("zuul.server.addr.main", "=" + port).getValue();
            if (sockAddr instanceof InetSocketAddress) {
                metricId = String.valueOf(((InetSocketAddress) sockAddr).getPort());
            } else {
                metricId = sockAddr.toString();
            }
        }

        ChannelConfig channelConfig = defaultChannelConfig("main");
        ChannelConfig channelDependencies = defaultChannelDependencies("main");
        channelConfig.set(CommonChannelConfigKeys.allowProxyHeadersWhen, StripUntrustedProxyHeadersHandler.AllowWhen.ALWAYS);
        channelConfig.set(CommonChannelConfigKeys.preferProxyProtocolForClientIp, false);
        channelConfig.set(CommonChannelConfigKeys.isSSlFromIntermediary, false);
        channelConfig.set(CommonChannelConfigKeys.withProxyProtocol, false);

        addrsToChannels.put(
                new NamedSocketAddress("http", sockAddr),
                new ZuulServerChannelInitializer(metricId, channelConfig, channelDependencies, clientChannels));
        logAddrConfigured(sockAddr);

        // WebSocket push service on port 7008
        SocketAddress pushSockAddr;
        String pushMetricId;
        {
            int pushPort = new DynamicIntProperty("zuul.server.port.http.push", 7008).get();
            pushSockAddr = new SocketAddressProperty("zuul.server.addr.http.push", "=" + pushPort).getValue();
            if (pushSockAddr instanceof InetSocketAddress) {
                pushMetricId = String.valueOf(((InetSocketAddress) pushSockAddr).getPort());
            } else {
                pushMetricId = pushSockAddr.toString();
            }
        }

        ChannelConfig pushChannelConfig = defaultChannelConfig("push");
        ChannelConfig pushChannelDependencies = defaultChannelDependencies("push");
        pushChannelConfig.set(CommonChannelConfigKeys.allowProxyHeadersWhen, StripUntrustedProxyHeadersHandler.AllowWhen.NEVER);
        pushChannelConfig.set(CommonChannelConfigKeys.preferProxyProtocolForClientIp, false);
        pushChannelConfig.set(CommonChannelConfigKeys.isSSlFromIntermediary, false);
        pushChannelConfig.set(CommonChannelConfigKeys.withProxyProtocol, false);
        pushChannelDependencies.set(ZuulDependencyKeys.pushConnectionRegistry, pushConnectionRegistry);

        addrsToChannels.put(
                new NamedSocketAddress("websocket", pushSockAddr),
                new SampleWebSocketPushChannelInitializer(pushMetricId, pushChannelConfig, pushChannelDependencies, clientChannels));
        logAddrConfigured(pushSockAddr);

        return Collections.unmodifiableMap(addrsToChannels);
    }
}
