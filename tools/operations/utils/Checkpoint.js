import fs from 'fs';
import _ from 'lodash';
import path from 'path';

export default class Checkpoint {
  constructor(outDir, fileName, campaignId) {
    this.outDir = outDir;
    this.fileName = fileName;
    this.campaignId = campaignId;

    this.data = {};
    this.filePath = path.resolve(this.outDir, this.fileName)
  }

  loadFile() {
    if (!fs.existsSync(this.filePath)) return;

    const lines = fs.readFileSync(this.filePath, 'utf-8').split('\n');

    _.each(lines, (line) => {
      const [lineCampaignId, lineEntryId] = line.split(',');

      if (!lineCampaignId && !lineEntryId) return;
      if (lineCampaignId !== this.campaignId) return;

      this.data[lineEntryId] = true;
    });
  }

  update(entryId) {
    const newRow = `${this.campaignId},${entryId}\n`;
    fs.appendFileSync(this.filePath, newRow);
    this.data[entryId] = true;
  }

  check(entryId) {
    return this.data[entryId];
  }
}
