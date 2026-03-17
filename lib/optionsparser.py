#!/usr/bin/python

import yaml
import os, sys
from lib.pluginsloader import PluginsLoader
from lib.proxylogger import ProxyLogger
from argparse import ArgumentParser

ProxyOptionsDefaultValues = {
}

ImpliedParams = {
    'plugin': ['redirector', ],
}


def parse_options(opts, version):
    global ProxyOptionsDefaultValues
    ProxyOptionsDefaultValues.update(opts)

    usage = "Usage: %%prog [options]"
    parser = ArgumentParser(usage=usage, prog="%prog " + version)

    parser.add_argument("-c", "--config", dest='config',
                        help="External configuration file. Defines values for below options, however specifying them on command line will supersed ones from file.")

    # General options
    parser.add_argument("-v", "--verbose", dest='verbose',
                        help="Displays verbose output.", action="store_true")
    parser.add_argument("-d", "--debug", dest='debug',
                        help="Displays debugging informations (implies verbose output).", action="store_true")
    parser.add_argument("-s", "--silent", dest='silent',
                        help="Suppresses all of the output logging.", action="store_true")
    parser.add_argument("-z", "--allow-invalid", dest='allow_invalid',
                        help="Process invalid HTTP requests. By default if a stream not resembling HTTP protocol reaches RedWardenLite listener - it will be dropped.",
                        action="store_true")
    parser.add_argument("-N", "--no-proxy", dest='no_proxy',
                        help="Disable standard HTTP/HTTPS proxy capability (will not serve CONNECT requests). Useful when we only need plugin to run.",
                        action="store_true")
    parser.add_argument("-W", "--tee", dest='tee',
                        help="While logging to output file, print to stdout also.", action="store_true")
    parser.add_argument("-w", "--output", dest='log',
                        help="Specifies output log file.", metavar="PATH", type=str)
    parser.add_argument("-A", "--access-log", dest='access_log',
                        help="Specifies where to write access attempts in Apache2 combined log format.", metavar="PATH",
                        type=str)
    parser.add_argument("--access-log-format", dest='access_log_format', default='apache2',
                        help="Specifies pre-defined format for access log lines. Supported values: apache2, redelk.",
                        choices=('apache2', 'redelk'), metavar="PATH", type=str)
    parser.add_argument("--redelk-backend-c2", dest='redelk_backend_name_c2', default='c2',
                        help="Backend name (label) for packets that are to be passed to C2 server. Must start with 'c2' phrase.",
                        metavar="NAME", type=str)
    parser.add_argument("--redelk-backend-decoy", dest='redelk_backend_name_decoy', default='decoy',
                        help="Backend name (label) for packets that are NOT to be passed to C2 server. Must start with 'decoy' phrase.",
                        metavar="NAME", type=str)
    parser.add_argument("-B", "--bind", dest='bind', metavar='NAME',
                        help="Specifies proxy's binding address along with protocol to serve (http/https). If scheme is specified here, don't add another scheme specification to the listening port number (123/https). Default: " +
                             opts['bind'] + ".",
                        type=str, default=opts['bind'])
    parser.add_argument("-P", "--port", dest='port', metavar='NUM',
                        help="Specifies proxy's binding port number(s). A value can be followed with either '/http' or '/https' to specify which type of server to bound on this port. Supports multiple binding ports by repeating this option: '--port 80 --port 443/https'. The port specification may also override globally used --bind address by preceding it with address and colon (--port 127.0.0.1:80/http). Default: " + str(
                            opts['port'][0]) + ".",
                        type=str, action="append", default=[])
    parser.add_argument("-t", "--timeout", dest='timeout', metavar='SECS',
                        help="Specifies timeout for proxy's response in seconds. Default: " + str(
                            opts['timeout']) + ".",
                        type=int, default=opts['timeout'])
    parser.add_argument("-u", "--proxy-url", dest='proxy_self_url', metavar='URL',
                        help="Specifies proxy's self url. Default: " + opts['proxy_self_url'] + ".",
                        type=str, default=opts['proxy_self_url'])
    parser.add_argument("--transport-mode", dest="transport_mode", metavar="MODE",
                        choices=("legacy", "async", "auto"),
                        help="Select upstream transport path. Default: {}.".format(opts['transport_mode']),
                        default=opts['transport_mode'])
    parser.add_argument("--transport-async-fallback", dest="transport_async_fallback_to_legacy_on_error",
                        help="When async mode fails for a request, fallback to legacy transport.",
                        action="store_true")
    parser.add_argument("--no-transport-async-fallback", dest="transport_async_fallback_to_legacy_on_error",
                        help="Disable legacy fallback when async request fails.",
                        action="store_false")
    parser.set_defaults(
        transport_async_fallback_to_legacy_on_error=opts.get('transport_async_fallback_to_legacy_on_error', True)
    )
    parser.add_argument("--transport-parity-enabled", dest="transport_parity_enabled",
                        help="Enable shadow parity checks between primary and alternate transport.",
                        action="store_true", default=opts.get('transport_parity_enabled', False))
    parser.add_argument("--transport-parity-header-ignore", dest="transport_parity_header_ignore",
                        help="Header to ignore in parity comparison (repeatable).", action="append",
                        default=opts.get('transport_parity_header_ignore', []))
    parser.add_argument("--transport-parity-allowlist-file", dest="transport_parity_allowlist_file",
                        metavar="PATH",
                        help="Path to static parity allowlist file.",
                        default=opts.get('transport_parity_allowlist_file', 'data/transport_parity_allowlist.json'))
    parser.add_argument("--transport-parity-artifact-dir", dest="transport_parity_artifact_dir",
                        metavar="DIR",
                        help="Directory for parity JSON/Markdown artifacts.",
                        default=opts.get('transport_parity_artifact_dir', 'artifacts/parity'))
    parser.add_argument("--transport-parity-ci-hard-fail", dest="transport_parity_ci_hard_fail",
                        help="Mark parity mismatches as CI hard-fail candidates.",
                        action="store_true", default=opts.get('transport_parity_ci_hard_fail', True))

    parser.add_argument("--runtime-profile", dest="runtime_profile", metavar="PROFILE",
                        choices=("compatible", "strict"),
                        help="Runtime hardening profile. Default: {}.".format(opts.get('runtime_profile', 'compatible')),
                        default=opts.get('runtime_profile', 'compatible'))
    parser.add_argument("--runtime-hardening-allow-unsafe", dest="runtime_hardening_allow_unsafe",
                        help="Allow strict-mode startup with unsafe runtime combinations (requires acknowledgement).",
                        action="store_true")
    parser.add_argument("--no-runtime-hardening-allow-unsafe", dest="runtime_hardening_allow_unsafe",
                        help="Disable strict-mode unsafe override.",
                        action="store_false")
    parser.set_defaults(
        runtime_hardening_allow_unsafe=opts.get('runtime_hardening_allow_unsafe', False)
    )
    parser.add_argument("--runtime-hardening-unsafe-ack", dest="runtime_hardening_unsafe_ack", metavar="TEXT",
                        help="Explicit acknowledgement for unsafe strict-mode override.",
                        default=opts.get('runtime_hardening_unsafe_ack', ''))
    parser.add_argument("--runtime-hardening-unsafe-ack-id", dest="runtime_hardening_unsafe_ack_ids",
                        metavar="ACK", action="append",
                        help="Per-check acknowledgement token for unsafe strict-mode override (repeatable).")
    parser.set_defaults(
        runtime_hardening_unsafe_ack_ids=opts.get('runtime_hardening_unsafe_ack_ids', [])
    )
    parser.add_argument("--runtime-hardening-validation-output", dest="runtime_hardening_validation_output",
                        metavar="MODE", choices=("human", "json"),
                        help="Startup hardening validation output mode. Default: {}.".format(
                            opts.get('runtime_hardening_validation_output', 'human')
                        ),
                        default=opts.get('runtime_hardening_validation_output', 'human'))

    parser.add_argument("--distributed-policy-enabled", dest="distributed_policy_enabled",
                        help="Enable distributed policy convergence artifact generation.",
                        action="store_true")
    parser.add_argument("--no-distributed-policy-enabled", dest="distributed_policy_enabled",
                        help="Disable distributed policy convergence artifact generation.",
                        action="store_false")
    parser.set_defaults(
        distributed_policy_enabled=opts.get('distributed_policy_enabled', False)
    )
    parser.add_argument("--distributed-policy-node-id", dest="distributed_policy_node_id", metavar="ID",
                        help="Node identifier used in distributed policy advertisements.",
                        default=opts.get('distributed_policy_node_id', 'node-local'))
    parser.add_argument("--distributed-policy-peer-node", dest="distributed_policy_peer_nodes",
                        metavar="NODE", action="append",
                        help="Peer node identifier for deterministic distributed policy simulations (repeatable).")
    parser.set_defaults(
        distributed_policy_peer_nodes=opts.get('distributed_policy_peer_nodes', [])
    )
    parser.add_argument("--distributed-policy-artifact-dir", dest="distributed_policy_artifact_dir",
                        metavar="DIR",
                        help="Artifact directory for distributed policy convergence outputs.",
                        default=opts.get('distributed_policy_artifact_dir', 'artifacts/distributed/policy'))
    parser.add_argument("--distributed-policy-retention-count", dest="distributed_policy_retention_count",
                        metavar="NUM", type=int,
                        help="How many policy convergence artifacts to retain.",
                        default=opts.get('distributed_policy_retention_count', 20))

    parser.add_argument("--fleet-telemetry-enabled", dest="fleet_telemetry_enabled",
                        help="Enable fleet telemetry aggregation artifact generation.",
                        action="store_true")
    parser.add_argument("--no-fleet-telemetry-enabled", dest="fleet_telemetry_enabled",
                        help="Disable fleet telemetry aggregation artifact generation.",
                        action="store_false")
    parser.set_defaults(
        fleet_telemetry_enabled=opts.get('fleet_telemetry_enabled', False)
    )
    parser.add_argument("--fleet-telemetry-artifact-dir", dest="fleet_telemetry_artifact_dir",
                        metavar="DIR",
                        help="Artifact directory for fleet telemetry snapshots.",
                        default=opts.get('fleet_telemetry_artifact_dir', 'artifacts/distributed/fleet'))
    parser.add_argument("--fleet-telemetry-retention-count", dest="fleet_telemetry_retention_count",
                        metavar="NUM", type=int,
                        help="How many fleet telemetry snapshots to retain.",
                        default=opts.get('fleet_telemetry_retention_count', 20))

    parser.add_argument("--observability-events-enabled", dest="observability_events_enabled",
                        help="Enable structured request event emission.",
                        action="store_true")
    parser.add_argument("--no-observability-events-enabled", dest="observability_events_enabled",
                        help="Disable structured request event emission.",
                        action="store_false")
    parser.set_defaults(
        observability_events_enabled=opts.get('observability_events_enabled', True)
    )
    parser.add_argument("--observability-events-file", dest="observability_events_file", metavar="PATH",
                        help="Path for JSONL structured request events.",
                        default=opts.get('observability_events_file', 'artifacts/observability/events.jsonl'))

    parser.add_argument("--observability-metrics-enabled", dest="observability_metrics_enabled",
                        help="Enable in-process metrics collection and exposition endpoint.",
                        action="store_true")
    parser.add_argument("--no-observability-metrics-enabled", dest="observability_metrics_enabled",
                        help="Disable in-process metrics collection and exposition endpoint.",
                        action="store_false")
    parser.set_defaults(
        observability_metrics_enabled=opts.get('observability_metrics_enabled', True)
    )
    parser.add_argument("--observability-metrics-path", dest="observability_metrics_path", metavar="PATH",
                        help="Path for metrics exposition endpoint.",
                        default=opts.get('observability_metrics_path', '/metrics'))
    parser.add_argument("--observability-metrics-format", dest="observability_metrics_format", metavar="FMT",
                        choices=("prometheus",),
                        help="Metrics exposition format. Default: {}.".format(
                            opts.get('observability_metrics_format', 'prometheus')
                        ),
                        default=opts.get('observability_metrics_format', 'prometheus'))
    parser.add_argument("--observability-metrics-access-mode", dest="observability_metrics_access_mode",
                        metavar="MODE", choices=("open", "loopback", "cidr"),
                        help="Metrics endpoint access policy. Default: {}.".format(
                            opts.get('observability_metrics_access_mode', 'open')
                        ),
                        default=opts.get('observability_metrics_access_mode', 'open'))
    parser.add_argument("--observability-metrics-allowed-cidr", dest="observability_metrics_allowed_cidrs",
                        metavar="CIDR",
                        help="Allowed CIDR for metrics endpoint when access mode is cidr (repeatable).",
                        action="append",
                        default=opts.get('observability_metrics_allowed_cidrs', []))
    parser.add_argument("--observability-event-include-query", dest="observability_event_include_query",
                        help="Include query string in structured event path field.",
                        action="store_true")
    parser.add_argument("--no-observability-event-include-query", dest="observability_event_include_query",
                        help="Exclude query string from structured event path field.",
                        action="store_false")
    parser.set_defaults(
        observability_event_include_query=opts.get('observability_event_include_query', False)
    )
    parser.add_argument("--observability-events-sampling-rate", dest="observability_events_sampling_rate",
                        metavar="RATE",
                        help="Deterministic sampling rate for structured events (0.0-1.0).",
                        type=float,
                        default=opts.get('observability_events_sampling_rate', 1.0))

    # SSL Interception
    sslgroup = parser.add_argument_group("SSL Interception setup")
    sslgroup.add_argument("-S", "--no-ssl-mitm", dest='no_ssl',
                          help="Turns off SSL interception/MITM and falls back on straight forwarding.",
                          action="store_true")
    sslgroup.add_argument('--ssl-certdir', dest='certdir', metavar='DIR',
                          help='Sets the destination for all of the SSL-related files, including keys, certificates (self and of' \
                               ' the visited websites). If not specified, a default value will be used to create a directory and remove it upon script termination. Default: "' +
                               opts['certdir'] + '"', default=opts['certdir'])
    sslgroup.add_argument('--ssl-cakey', dest='cakey', metavar='NAME',
                          help='Specifies this proxy server\'s (CA) certificate private key. Default: "' + opts[
                              'cakey'] + '"', default=opts['cakey'])
    sslgroup.add_argument('--ssl-cacert', dest='cacert', metavar='NAME',
                          help='Specifies this proxy server\'s (CA) certificate. Default: "' + opts['cacert'] + '"',
                          default=opts['cacert'])
    sslgroup.add_argument('--ssl-certkey', dest='certkey', metavar='NAME',
                          help='Specifies CA certificate\'s public key. Default: "' + opts['certkey'] + '"',
                          default=opts['certkey'])
    sslgroup.add_argument('--ssl-cacn', dest='cacn', metavar='CN',
                          help='Sets the common name of the proxy\'s CA authority. If this option is not set, will use --hostname instead. It is required only when no --ssl-cakey/cert were specified and RedWardenLite will need to generate ones automatically. Default: "' +
                               opts['cacn'] + '"', default=opts['cacn'])

    # Plugins handling
    plugins = parser.add_argument_group("Plugins handling")
    plugins.add_argument('-L', '--list-plugins', action='store_true', help='List available plugins.')
    plugins.add_argument('-p', '--plugin', dest='plugin', action='append', metavar='PATH', type=str,
                         help="Specifies plugin's path to be loaded.")
    plugins.add_argument('--plugin-api-version', dest='plugin_api_version', metavar='VER', type=str,
                         help='Runtime plugin API compatibility version.',
                         default=opts.get('plugin_api_version', '1.0'))
    plugins.add_argument('--plugin-require-capabilities', dest='plugin_require_capabilities',
                         help='Require formal plugin capability metadata during plugin load.',
                         action='store_true')
    plugins.add_argument('--no-plugin-require-capabilities', dest='plugin_require_capabilities',
                         help='Allow loading legacy plugins without formal capability metadata.',
                         action='store_false')
    plugins.set_defaults(
        plugin_require_capabilities=opts.get('plugin_require_capabilities', True)
    )
    plugins.add_argument('--plugin-isolation-enabled', dest='plugin_isolation_enabled',
                         help='Enable runtime plugin execution isolation boundaries.',
                         action='store_true')
    plugins.add_argument('--no-plugin-isolation-enabled', dest='plugin_isolation_enabled',
                         help='Disable runtime plugin execution isolation boundaries.',
                         action='store_false')
    plugins.set_defaults(
        plugin_isolation_enabled=opts.get('plugin_isolation_enabled', True)
    )
    plugins.add_argument('--plugin-isolation-failure-mode', dest='plugin_isolation_failure_mode',
                         metavar='MODE', choices=('fail_closed', 'fail_open'),
                         help='Plugin isolation failure behavior. Default: {}.'.format(
                             opts.get('plugin_isolation_failure_mode', 'fail_closed')
                         ),
                         default=opts.get('plugin_isolation_failure_mode', 'fail_closed'))

    feed_with_plugin_options(opts, parser)

    params = parser.parse_args()

    for k, v in ImpliedParams.items():
        setattr(params, k, v)

    if hasattr(params, 'config') and params.config != '':
        try:
            params = parseParametersFromConfigFile(params)
        except Exception as e:
            parser.error(str(e))

        opts.update(params)
    else:
        opts.update(vars(params))

    if opts['list_plugins']:
        files = sorted(
            [f for f in os.scandir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../plugins/'))],
            key=lambda f: f.name)
        for _, entry in enumerate(files):
            if entry.name.endswith(".py") and entry.is_file() and entry.name.lower() not in ['iproxyplugin.py',
                                                                                             '__init__.py']:
                print('[+] Plugin: {}'.format(entry.name))

        sys.exit(0)

    if opts['plugin'] != None and len(opts['plugin']) > 0:
        for i, opt in enumerate(opts['plugin']):
            decomposed = PluginsLoader.decompose_path(opt)
            if not os.path.isfile(decomposed['path']):
                opt = opt.replace('.py', '')
                opt2 = os.path.normpath(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), '../plugins/{}.py'.format(opt)))
                if not os.path.isfile(opt2):
                    raise Exception('Specified plugin: "%s" does not exist.' % decomposed['path'])
                else:
                    opt = opt2

            opts['plugins'].add(opt)

    if opts['silent'] and opts['log']:
        parser.error("Options -s and -w are mutually exclusive.")

    if opts['silent']:
        opts['log'] = 'none'
    elif opts['log'] and len(opts['log']) > 0:
        try:
            if not os.path.isfile(opts['log']):
                with open(opts['log'], 'w') as f:
                    pass
            opts['log'] = opts['log']

        except Exception as e:
            raise Exception('[ERROR] Failed to open log file for writing. Error: "%s"' % e)
    else:
        opts['log'] = sys.stdout

    if opts['log'] and opts['log'] != sys.stdout:
        opts['log'] = os.path.normpath(opts['log'])

    if opts['cakey']:
        opts['cakey'] = os.path.normpath(opts['cakey'])

    if opts['certdir']:
        opts['certdir'] = os.path.normpath(opts['certdir'])

    if opts['certkey']:
        opts['certkey'] = os.path.normpath(opts['certkey'])

    if 'redelk_backend_name_c2' in opts.keys():
        if not opts['redelk_backend_name_c2'].startswith('c2'):
            raise Exception('[ERROR] redelk_backend_name_c2 option must start with "c2"!')

    if 'redelk_backend_name_decoy' in opts.keys():
        if not opts['redelk_backend_name_decoy'].startswith('decoy'):
            raise Exception('[ERROR] redelk_backend_name_decoy option must start with "decoy"!')

    if 'redelk_backend_name_c2' in opts.keys() and 'redelk_backend_name_decoy' in opts.keys():
        if opts['redelk_backend_name_c2'].find(' ') != -1 or opts['redelk_backend_name_decoy'].find(' ') != -1:
            raise Exception(
                '[ERROR] redelk_backend_name_c2 and redelk_backend_name_decoy options cannot contain spaces!')


def parseParametersFromConfigFile(_params):
    parametersRequiringDirectPath = (
        'log',
        'output',
        'access_log',
        'certdir',
        'certkey',
        'cakey',
        'cacert',
        'ssl_certdir',
        'ssl_certkey',
        'ssl_cakey',
        'ssl_cacert',
        'transport_parity_allowlist_file',
        'transport_parity_artifact_dir',
        'observability_events_file',
        'distributed_policy_artifact_dir',
        'fleet_telemetry_artifact_dir',
    )

    parametersWithPathThatMayNotExist = (
        'log',
        'output',
        'access_log',
        'ssl_certdir',
        'transport_parity_allowlist_file',
        'transport_parity_artifact_dir',
        'observability_events_file',
        'distributed_policy_artifact_dir',
        'fleet_telemetry_artifact_dir',
    )

    translateParamNames = {
        'output': 'log',
        'proxy_url': 'proxy_self_url',
        'no_ssl_mitm': 'no_ssl',
        'ssl_certdir': 'certdir',
        'ssl_certkey': 'certkey',
        'ssl_cakey': 'cakey',
        'ssl_cacert': 'cacert',
        'ssl_cacn': 'cacn',
        'drop_invalid_http_requests': 'allow_invalid',
        'redelk_frontend': 'redelk_frontend_name',
        'redelk_backend_c2': 'redelk_backend_name_c2',
        'redelk_backend_decoy': 'redelk_backend_name_decoy',
        'throttle_peer_logging': 'throttle_down_peer_logging',
        'proxypass': 'proxy_pass',
        'anti_replay_attack': 'mitigate_replay_attack',
    }

    valuesThatNeedsToBeList = (
        'port',
        'plugin',
        'observability_metrics_allowed_cidrs',
        'runtime_hardening_unsafe_ack_ids',
        'distributed_policy_peer_nodes',
    )

    outparams = vars(_params)
    config = {}
    configBasePath = ''

    if outparams['config'] != None and len(outparams['config']) > 0:
        if not 'config' in outparams.keys() or not os.path.isfile(outparams['config']):
            raise Exception(f'RedWarden config file not found: ({outparams["config"]}) or --config not specified!')
    else:
        return outparams

    try:
        with open(outparams['config']) as f:
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                raise Exception(f'Could not parse YAML config file:\n\n{e}\n\n')

        outparams.update(config)

        for val in valuesThatNeedsToBeList:
            if val in outparams.keys() and val in config.keys():
                if type(config[val]) == str:
                    outparams[val] = [config[val], ]
                else:
                    outparams[val] = config[val]

        for k, v in ProxyOptionsDefaultValues.items():
            if k not in outparams.keys():
                outparams[k] = v

        for k, v in translateParamNames.items():
            if k in outparams.keys():
                outparams[v] = outparams[k]
            if v in outparams.keys():
                outparams[k] = outparams[v]

        configBasePath = os.path.dirname(os.path.abspath(outparams['config']))

        for paramName in parametersRequiringDirectPath:
            if paramName in outparams.keys() and \
                    outparams[paramName] != '' and outparams[paramName] != None:
                p1 = outparams[paramName]
                if not os.path.isfile(outparams[paramName]):
                    outparams[paramName] = os.path.join(configBasePath, outparams[paramName])
                    p = ''
                    if paramName in translateParamNames.values():
                        p = list(translateParamNames.keys())[list(translateParamNames.values()).index(paramName)]

                    if not os.path.isfile(outparams[paramName]) and \
                            not ((paramName in parametersWithPathThatMayNotExist) or (
                                    p in parametersWithPathThatMayNotExist)):
                        p2 = outparams[paramName]
                        raise Exception(
                            f'\n\nCould not find file pointed to by "{paramName}" / "{p}" parameter in specified config file!\nTried these paths:\n\t- {p1}\n\t- {p2}\n\nMake sure to correct the path of this parameter in your config file.')

        return outparams

    except FileNotFoundError as e:
        raise Exception(f'RedWardenLite config file not found: ({outparams["config"]})!')

    except Exception as e:
        raise Exception(f'Unhandled exception occurred while parsing RedWardenLite config file: {e}')

    return outparams


def feed_with_plugin_options(opts, parser):
    logger = ProxyLogger()
    plugins = []
    files = sorted([f for f in os.scandir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../plugins/'))],
                   key=lambda f: f.name)
    for _, entry in enumerate(files):
        if entry.name.endswith(".py") and entry.is_file() and entry.name.lower() not in ['iproxyplugin.py',
                                                                                         '__init__.py']:
            plugins.append(entry.path)

    options = opts.copy()
    options['plugins'] = plugins
    options['verbose'] = True
    options['debug'] = False

    plugin_own_options = {}

    pl = PluginsLoader(logger, options)
    for name, plugin in pl.get_plugins().items():
        logger.dbg("Fetching plugin {} options.".format(name))
        if hasattr(plugin, 'help'):
            plugin_options = parser.add_argument_group("Plugin '{}' options".format(plugin.get_name()))
            plugin.help(plugin_options)
