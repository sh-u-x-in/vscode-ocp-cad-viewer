/* eslint-disable @typescript-eslint/naming-convention */
/*
   Copyright 2025 Bernhard Walter
  
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

import * as vscode from "vscode";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as output from "./output";
import { IncomingMessage } from "http";
import AdmZip from "adm-zip";
import { https } from "follow-redirects";

export async function download(library: string, destination: string) {
    const timeout = 10000;
    const exampleDownloads =
        vscode.workspace.getConfiguration("OcpCadViewer.advanced")["exampleDownloads"];

    const archiveUrl = exampleDownloads[library]["zip"];
    output.info(`extension.downloadExample: Example download URL: ${archiveUrl}`);
    const examplePath = exampleDownloads[library]["example_path"];
    const filename = path.basename(archiveUrl);
    const targetPath = path.join(destination, `${library}_examples`);
    output.info(`extension.downloadExample: Target path: ${targetPath}`);

    let request = https.get(archiveUrl, (response: IncomingMessage) => {
        if (response.statusCode === 200) {
            const tempFolder = path.join(os.tmpdir(), "cadquery-viewer");
            fs.mkdtemp(tempFolder, (err, folder) => {
                if (err) {
                    vscode.window.showErrorMessage(
                        vscode.l10n.t("Cannot create temp folder {0}", folder)
                    );
                    return;
                }
                const downloadPath = path.join(folder, filename);
                var stream = fs.createWriteStream(downloadPath);
                response.pipe(stream);

                stream.on("finish", () => {
                    stream.close();
                    vscode.window.showInformationMessage(
                        vscode.l10n.t('File "{0}" downloaded successfully.', archiveUrl)
                    );
                    output.info(`extension.downloadExample: Archive URL ${archiveUrl} downloaded`);
                    try {
                        const zip = new AdmZip(downloadPath);
                        zip.extractAllTo(folder, true);
                        output.info(`extension.downloadExample: Archive unzipped to ${folder}`);
                    } catch (error) {
                        vscode.window.showErrorMessage(
                            vscode.l10n.t('Unzipping "{0}" failed.', downloadPath)
                        );
                        output.error(
                            `extension.downloadExample: Unzipping "${downloadPath}" failed: ${error}`
                        );
                        return;
                    }
                    fs.rename(path.join(folder, examplePath), targetPath, (err) => {
                        if (err) {
                            vscode.window.showErrorMessage(
                                vscode.l10n.t('Moving examples to "{0}" failed.', targetPath)
                            );
                            output.error(
                                `extension.downloadExample: Moving examples to "${targetPath}" failed: ${err}`
                            );
                        } else {
                            vscode.window.showInformationMessage(
                                vscode.l10n.t(
                                    'Examples successfully downloaded to "{0}".',
                                    targetPath
                                )
                            );
                            output.info(
                                `extension.downloadExample: Examples successfully downloaded to "${targetPath}".`
                            );
                        }
                    });
                });
            });
        } else {
            vscode.window.showErrorMessage(
                vscode.l10n.t("Cannot download {0}", archiveUrl)
            );
            output.error(
                `extension.downloadExample: ${archiveUrl} ${response.statusMessage} (${response.statusCode})`
            );
        }
    });

    request.setTimeout(timeout, function () {
        request.destroy();
    });

    request.on("error", function (e: any) {
        vscode.window.showErrorMessage(vscode.l10n.t("Cannot download {0}", archiveUrl));
        output.error(`extension.downloadExample: Cannot download ${archiveUrl} ${e}`);
    });
}
