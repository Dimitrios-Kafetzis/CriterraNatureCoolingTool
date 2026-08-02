#!/usr/bin/env bash
# The STATIC half of the no-third-party-request gate (D-030, D-035, D-047.1,
# D-048.6; runtime companion added by D-049.8).
#
# The rule is one of the reasons this tool is deployable inside institutions
# with restrictive networks, so it is machine-checked rather than remembered.
# Since v2.2 the rule reads: the package makes no third-party request until a
# DEPLOYER configures one, or a user opts in (D-049.1). That configuration is
# runtime state — two environment variables — and never appears in the build
# output, so this static check's claim is unchanged: NO third-party URL may
# sit in a published artefact in a position the browser fetches. A literal
# tile host in the build would mean something is fetched without an operator
# having configured it, which is exactly what the rule forbids.
#
# What greps cannot state is what a running deployment actually requests;
# tools/check_runtime_requests.py drives the built app headlessly and asserts
# that — zero external requests unconfigured, only-the-configured-host when
# configured, graceful degradation when the host is unreachable. The two
# checks together replace what was, before v2.2, this file alone.
#
# It checks the two published artefacts: the documentation site and the
# production frontend build.
#
#     tools/check_no_third_party_requests.sh site frontend/dist
#
# What it looks for is what actually causes a request — an absolute URL in a
# position the browser fetches — and not merely the appearance of a URL. A
# grep for "https?://" over a bundled JavaScript file finds XML namespace
# identifiers, React's error-documentation links and the footer's own brand
# link, none of which are requests; a check that cried wolf over those would be
# switched off within a month.

set -euo pipefail

status=0

fail() {
    echo "FAIL: $1"
    status=1
}

for target in "$@"; do
    if [ ! -d "$target" ]; then
        echo "no such directory: $target" >&2
        exit 2
    fi
    echo "Checking $target"

    # 1. Markup that fetches: src, and the link relations that load resources.
    if grep -rEn 'src="https?://' "$target" --include='*.html'; then
        fail "$target: an element loads a resource from an absolute URL"
    fi
    if grep -rEn '<link[^>]*rel="(stylesheet|preload|prefetch|dns-prefetch|preconnect)"[^>]*href="https?://' \
        "$target" --include='*.html'; then
        fail "$target: a link element points at a third-party resource"
    fi

    # 2. Stylesheets that fetch: url() and @import. This is how a web font or a
    #    background image sneaks back in after being deliberately self-hosted.
    if grep -rEn 'url\(\s*["'"'"']?https?://' "$target" --include='*.css'; then
        fail "$target: a stylesheet loads a resource from an absolute URL"
    fi
    if grep -rEn '@import\s+(url\()?\s*["'"'"']https?://' "$target" --include='*.css'; then
        fail "$target: a stylesheet imports from an absolute URL"
    fi

    # 3. Script that fetches. A bundled application cannot be checked by
    #    grepping for URLs, so the check is narrower and aimed at the thing
    #    that would actually be added: a hard-coded endpoint handed to fetch,
    #    XMLHttpRequest.open, importScripts, or an Image/script src assignment.
    if grep -rEn \
        '(fetch\(|\.open\(["'"'"'](GET|POST|PUT|PATCH|DELETE)["'"'"'],\s*|importScripts\()\s*["'"'"'`]https?://' \
        "$target" --include='*.js'; then
        fail "$target: script code requests an absolute URL"
    fi
    if grep -rEn '\.src\s*=\s*["'"'"'`]https?://' "$target" --include='*.js'; then
        fail "$target: script code assigns an absolute URL to a src property"
    fi
done

if [ "$status" -ne 0 ]; then
    cat <<'EOF'

The default build must make no third-party request (D-030, D-035, D-047.1).

If this is the opt-in tile layer of D-047.1, it must not appear here: that
layer is built from a template a user types at runtime, so nothing about it is
present in the build output. A literal URL reaching the build means something
is fetched without the user having asked for it, which is the thing the rule
forbids.
EOF
    exit 1
fi

echo "OK: no third-party request in $*"
