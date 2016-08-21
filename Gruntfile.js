module.exports = function(grunt) {

  // load plugins as needed instead of up front
  require('jit-grunt')(grunt);

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
      dist: {
        files: {
          'static/dist/css/app.built.css': [
            'static/sass/main.scss',
            'static/sass/pokemon-sprite.scss'
          ],
          'static/dist/css/mobile.built.css': 'static/sass/mobile.scss',
          'static/dist/css/statistics.built.css': 'static/css/statistics.css'
        }
      }
    },
    eslint: {
      src: ['static/js/*.js', '!js/vendor/**/*.js']
    },
    babel: {
      options: {
        sourceMap: true,
        presets: ['es2015']
      },
      dist: {
        files: {
          'static/dist/js/app.built.js': 'static/js/app.js',
          'static/dist/js/map.built.js': 'static/js/map.js',
          'static/dist/js/mobile.built.js': 'static/js/mobile.js',
          'static/dist/js/stats.built.js': 'static/js/stats.js',
          'static/dist/js/statistics.built.js': 'static/js/statistics.js',
          'static/dist/js/push.custom.built.js': 'static/js/vendor/push.custom.js'
        }
      }
    },
    uglify: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n',
        sourceMap: true,
        compress: {
          unused: false
        }
      },
      build: {
        files: {
          'static/dist/js/app.min.js': 'static/dist/js/app.built.js',
          'static/dist/js/map.min.js': 'static/dist/js/map.built.js',
          'static/dist/js/mobile.min.js': 'static/dist/js/mobile.built.js',
          'static/dist/js/stats.min.js': 'static/dist/js/stats.built.js',
          'static/dist/js/statistics.min.js': 'static/dist/js/statistics.built.js',
          'static/dist/js/push.custom.min.js': 'static/js/vendor/push.custom.js'
        }
      }
    },
    minjson: {
      build: {
        files: {
          'static/dist/data/pokemon.min.json': 'static/data/pokemon.json',
          'static/dist/data/mapstyle.min.json': 'static/data/mapstyle.json',
          'static/dist/data/searchmarkerstyle.min.json': 'static/data/searchmarkerstyle.json',
          'static/dist/data/notificationdistance.min.json': 'static/data/notificationdistance.json',
          'static/sounds/audiosprites.min.json': 'static/data/sounds/audiosprites.json',
          'static/sounds/default/audiosprite_default.min.json': 'static/data/sounds/audiosprite_default.json',
          'static/sounds/cries/audiosprite_cries.min.json': 'static/data/sounds/audiosprite_cries.json',
          'static/dist/locales/de.min.json': 'static/locales/de.json',
          'static/dist/locales/fr.min.json': 'static/locales/fr.json',
          'static/dist/locales/ja.min.json': 'static/locales/ja.json',
          'static/dist/locales/pt_br.min.json': 'static/locales/pt_br.json',
          'static/dist/locales/ru.min.json': 'static/locales/ru.json',
          'static/dist/locales/zh_cn.min.json': 'static/locales/zh_cn.json',
          'static/dist/locales/zh_tw.min.json': 'static/locales/zh_tw.json',
          'static/dist/locales/zh_hk.min.json': 'static/locales/zh_hk.json'
        }
      }
    },
    clean: {
      build: {
        src: ['static/dist', 'static/sounds/**/*.json']
      }
    },
    watch: {
      options: {
        interval: 1000,
        spawn: true
      },
      js: {
        files: ['static/js/**/*.js'],
        options: { livereload: true },
        tasks: ['js-lint', 'js-build']
      },
      json: {
        files: ['static/data/*.json', 'static/data/sounds/*.json', 'static/locales/*.json'],
        options: { livereload: true },
        tasks: ['json']
      },
      css: {
        files: '**/*.scss',
        options: { livereload: true },
        tasks: ['css-build']
      }
    },
    cssmin: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
      },
      build: {
        files: {
          'static/dist/css/app.min.css': 'static/dist/css/app.built.css',
          'static/dist/css/mobile.min.css': 'static/dist/css/mobile.built.css',
          'static/dist/css/statistics.min.css': 'static/dist/css/statistics.built.css'
        }
      }
    }
  });

  grunt.registerTask('js-build', ['newer:babel', 'newer:uglify']);
  grunt.registerTask('css-build', ['newer:sass', 'newer:cssmin']);
  grunt.registerTask('js-lint', ['newer:eslint']);
  grunt.registerTask('json', ['newer:minjson']);

  grunt.registerTask('build', ['clean', 'js-build', 'css-build', 'json']);
  grunt.registerTask('lint', ['js-lint']);
  grunt.registerTask('default', ['build', 'watch']);

};
