function initMap() {
    function e(e) {
        var t = b.getProjection(),
        a = e.marker,
        n = t.fromLatLngToContainerPixel(a);
        return n
    }
    function t(t, a, n) {
        var s = e(t),
        o = parseInt(s.x),
        r = parseInt(s.y) - 20;
        if (!(10 > o || 10 > r || o > $(window).width() || r > $(window).height())) {
            var i = parseInt(10000 * Math.random());
            $('.map-wrap').append('<div class="numbers-popup ' + a + '" id="np' + i + '" style="top:' + r + 'px; left:' + o + 'px;">' + n + '</div>'),
            window.setTimeout(function () {
                $('#np' + i).addClass('fade')
            }, 600),
            window.setTimeout(function () {
                $('#np' + i).remove()
            }, 4000)
        }
    }
    function a(e) {
        return '<span class="team highlight t' + e + '">' + L[e] + '</span>'
    }
    function n(e, t) {
        return '<span class="gym highlight" data-id="' + t + '">' + e + '</span>'
    }
    function s(e) {
        return e.substring(11, 19)
    }
    function o(e, t) {
        $('.feed').prepend('<li>' + e + ' <span class="time">' + s(t) + '</span></li>'),
        i()
    }
    function r(e) {
        return $('#' + e.substring(0, 32))
    }
    function i() {
        $('.gym').mouseenter(function () {
            var e = $(this).data('id'),
            t = r(e);
            t.addClass('highlight')
        }),
        $('.gym').mouseleave(function () {
            var e = $(this).data('id'),
            t = r(e);
            t.removeClass('highlight')
        }),
        $('.gym').click(function () {
            var e = $(this).data('id'),
            t = m(e),
            a = new google.maps.LatLng(t.coords[0], t.coords[1]);
            T.panTo(a)
        })
    }
    function l() {
        function e(e, t) {
            return $(t).data('percentage') > $(e).data('percentage') ? 1 : - 1
        }
        for (var t = C.length, a = {
            0: 0,
            1: 0,
            2: 0,
            3: 0
        }, n = 0; n < C.length; n++) a[C[n].team]++;
        for (var n = 0; n < Object.keys(a).length; n++) {
            var s = a[n],
            o = s / t,
            r = (100 * o).toFixed(1);
            $('.team-' + n).data('percentage', r),
            $('.team-' + n + ' .percentage').text(r + '%'),
            $('.team-' + n + ' .gyms').text(s + ' gyms')
        }
        $('.team-stats li').sort(e).appendTo('.team-stats')
    }
    function d(e) {
        var t = new google.maps.LatLng(e.coords[0], e.coords[1]);
        return e.marker = t,
        t
    }
    function m(e) {
        for (var t = 0; t < C.length; t++) if (C[t].id == e) return C[t];
        return null
    }
    function c(e) {
        var t = {
        };
        t.id = e[0],
        t.coords = [
            e[1],
            e[2]
        ],
        t.team = e[3],
        t.points = e[4],
        t.updated = e[5],
        t.name = e[6],
        d(t),
        C.push(t),
        teams[t.team]++
    }
    function u(e) {
        var s = m(e[0]);
        if (s.points != e[4] || s.team != e[3]) {
            var r = $('#' + s.id.substring(0, 32)),
            i = $('#dot-' + s.id.substring(0, 32)),
            l = 'white',
            c = !1;
            if (s.team != e[3]) 0 == s.team ? o(a(e[3]) + ' zdobyli gym ' + n(s.name, s.id), e[5])  : 0 == e[3] ? o(a(s.team) + ' stracili gym ' + n(s.name, s.id), e[5])  : o(a(e[3]) + ' odbili gym ' + n(s.name, s.id) + ' od ' + a(s.team), e[5]),
            c = !0,
            t(s, 'pokonani', 'pokonani');
             else if (s.points != e[4]) {
                var u = e[4] - s.points;
                u > 0 ? (o(a(s.team) + ' podnieśli prestiż ' + n(s.name, s.id) + ' (+' + u + ')', e[5]), t(s, 'good', '+' + u), l = 'intense')  : (o(a(s.team) + ' są atakowani ' + n(s.name, s.id) + ' (' + u + ')', e[5]), t(s, 'bad', u))
            }
            var g = s.team;
            s.team = e[3],
            s.points = e[4],
            s.updated = e[5],
            c || d(s),
            r.addClass(l),
            window.setTimeout(function () {
                r.removeClass(l),
                c && (r.addClass('intense'), window.setTimeout(function () {
                    r.removeClass('t' + g),
                    r.addClass('t' + s.team),
                    i.removeClass('t' + g),
                    i.addClass('t' + s.team),
                    d(s),
                    window.setTimeout(function () {
                        r.removeClass('intense')
                    }, 800)
                }, 600))
            }, 300)
        }
    }
    function g() {
        C = [
        ],
        teams = {
            0: 0,
            1: 0,
            2: 0,
            3: 0
        },
        $.getJSON('gyms.php', function (e) {
            for (var t = 0; t < e.gyms.length; t++) {
                var a = e.gyms[t];
                c(a)
            }
            y(C),
            l(),
            lastServerUpdateTimestamp = e.timestamp
        })
    }
    function p() {
        $.getJSON('gyms.php?after=' + lastServerUpdateTimestamp, function (e) {
            for (var t = 0; t < e.gyms.length; t++) {
                var a = e.gyms[t];
                console.log(a),
                k.push(a)
            }
            e.gyms.length > 0 && l(),
            lastServerUpdateTimestamp = e.timestamp
        })
    }
    function f() {
        k.length < 1 || (u(k[0]), k.shift())
    }
    function y(e) {
        w = new google.maps.OverlayView,
        w.onAdd = function () {
            var t = d3.select(this.getPanes().overlayMouseTarget).append('div').attr('class', 'overlay'),
            a = t.append('svg'),
            n = a.append('g').attr('class', 'Gyms');
            w.draw = function () {
                var t = this,
                a = t.getProjection(),
                s = function (e) {
                    var t = new google.maps.LatLng(e[0], e[1]),
                    n = a.fromLatLngToDivPixel(t);
                    return [n.x + 4000,
                    n.y + 4000]
                },
                o = [
                ];
                e.forEach(function (e) {
                    o.push(s(e.coords))
                });
                var r = d3.geom.voronoi(o),
                i = {
                    d: function (e, t) {
                        return 'M' + r[t].join('L') + 'Z'
                    }
                };
                n.selectAll('path').data(e).attr(i).enter().append('svg:path').attr('class', function (e) {
                    return 'cell t' + e.team
                }).attr(i).attr('id', function (e) {
                    return e.id.substring(0, 32)
                }).on('mouseover', function (e) {
                    $('#dot-' + e.id.substring(0, 32)).addClass('highlight')
                }).on('mouseout', function (e) {
                    $('#dot-' + e.id.substring(0, 32)).removeClass('highlight')
                });
                var l = {
                    cx: function (e, t) {
                        return o[t][0]
                    },
                    cy: function (e, t) {
                        return o[t][1]
                    },
                    r: function () {
                        return 2
                    }
                };
                n.selectAll('circle').data(e).attr(l).enter().append('svg:circle').attr(l).attr('class', function (e) {
                    return 'dot t' + e.team
                }).attr('id', function (e) {
                    return 'dot-' + e.id.substring(0, 32)
                }).on('mouseover', function (e) {
                    v(e, $(this))
                }).on('mouseout', function () {
                    h($(this))
                })
            }
        },
        w.setMap(T)
    }
    function v(e, t) {
        t.addClass('hovered'),
        console.log(e)
    }
    function h(e) {
        e.removeClass('hovered')
    }
    var T,
    w,
    b,
    C,
    k = [
    ],
    L = {
        0: 'Gym',
        1: 'Mystic',
        2: 'Valor',
        3: 'Instinct'
    };
    $('.stats-toggle').click(function () {
        $('body').addClass('stats-active'),
        $('body').removeClass('feed-active'),
        $('body').removeClass('map-active')
    }),
    $('.map-toggle').click(function () {
        $('body').addClass('map-active'),
        $('body').removeClass('stats-active'),
        $('body').removeClass('feed-active')
    }),
    $('.feed-toggle').click(function () {
        $('body').addClass('feed-active'),
        $('body').removeClass('stats-active'),
        $('body').removeClass('map-active')
    }),
    $('.about-toggle').click(function (e) {
        return $('body').hasClass('about-active') ? $('body').removeClass('about-active')  : $('body').addClass('about-active'),
        e.preventDefault(),
        !1
    });
    var x = document.getElementById('map-canvas'),
    M = {
        center: new google.maps.LatLng(53.12, 18.03),
        zoom: 14,
        streetViewControl: !1,
        minZoom: 10,
        styles: [
            {
                featureType: 'all',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#282727'
                    }
                ]
            },
            {
                featureType: 'all',
                elementType: 'labels.text.fill',
                stylers: [
                    {
                        saturation: 36
                    },
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 40
                    }
                ]
            },
            {
                featureType: 'all',
                elementType: 'labels.text.stroke',
                stylers: [
                    {
                        visibility: 'on'
                    },
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 16
                    }
                ]
            },
            {
                featureType: 'all',
                elementType: 'labels.icon',
                stylers: [
                    {
                        visibility: 'off'
                    }
                ]
            },
            {
                featureType: 'administrative',
                elementType: 'geometry.fill',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 20
                    }
                ]
            },
            {
                featureType: 'administrative',
                elementType: 'geometry.stroke',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 17
                    },
                    {
                        weight: 1.2
                    }
                ]
            },
            {
                featureType: 'landscape',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 20
                    }
                ]
            },
            {
                featureType: 'poi',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 21
                    }
                ]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry.fill',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 17
                    }
                ]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry.stroke',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 29
                    },
                    {
                        weight: 0.2
                    }
                ]
            },
            {
                featureType: 'road.arterial',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 18
                    }
                ]
            },
            {
                featureType: 'road.local',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 16
                    }
                ]
            },
            {
                featureType: 'transit',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 19
                    }
                ]
            },
            {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [
                    {
                        color: '#000000'
                    },
                    {
                        lightness: 17
                    }
                ]
            }
        ]
    };
    T = new google.maps.Map(x, M),
    b = new google.maps.OverlayView,
    b.draw = function () {
    },
    b.setMap(T),
    g(),
    window.setInterval(p, 8000),
    window.setInterval(f, 1600)
}
