import argparse
import os
import sys

import uvicorn

if __name__ == '__main__':
    app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    project_dir = os.path.realpath(os.path.join(os.path.realpath(app_path), os.pardir))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        dest='host',
        type=str,
        required=False,
        default='0.0.0.0',
        help='Host where server started'
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        type=int,
        required=False,
        default=5000,
        help='Port number'
    )
    parser.add_argument(
        '-ll', '--log-level',
        dest='log_level',
        type=str,
        choices=('debug', 'info', 'warning', 'error'),
        required=False,
        default='warning',
        help='Logging level (debug - maximum messages, error - only errors)'
    )
    parser.add_argument(
        '--workers',
        dest='workers',
        type=int,
        required=False,
        default=1,
        help='Server workers'
    )
    parser.add_argument(
        '--reload',
        dest='reload',
        type=int,
        required=False,
        default=0,
        help='Auto reload'
    )
    args = parser.parse_args()
    os.environ['AUTORUN_MIGRATIONS'] = '1'

    # import app.settings

    # AUTORUN_MIGRATIONS
    from alembic import command, config

    alembic_cfg = config.Config()
    alembic_cfg.set_main_option("script_location", "app:migrations")
    command.upgrade(alembic_cfg, 'head')

    import app.main  # noqa, required for running with pyinstaller

    print(f'Start Server on {args.host}:{args.port} LOG LEVEL: {args.log_level}')
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        workers=args.workers,
        reload=(args.reload == 1),
    )
