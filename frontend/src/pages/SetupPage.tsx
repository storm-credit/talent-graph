import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import type { IndustryTemplate } from "../types";
import { motion } from "framer-motion";
import { Building2, Factory, Code, TrendingUp, Heart, Banknote, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

const industryIcons: Record<string, React.ElementType> = {
  tech_startup: Code,
  enterprise_it: Building2,
  consulting: TrendingUp,
  manufacturing: Factory,
  finance: Banknote,
  healthcare: Heart,
};

const growthStages = ["early", "growth", "mature", "enterprise"] as const;
const cultureTypes = ["clan", "adhocracy", "market", "hierarchy"] as const;

export function SetupPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const navigate = useNavigate();

  const [step, setStep] = useState(0);
  const [templates, setTemplates] = useState<IndustryTemplate[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [numPeople, setNumPeople] = useState(15);
  const [growthStage, setGrowthStage] = useState("growth");
  const [cultureType, setCultureType] = useState("adhocracy");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getTemplates().then(setTemplates).catch(() => {});
  }, []);

  const selectedTemplate = templates.find((t) => t.industry === selectedIndustry);

  const handleCreate = async () => {
    if (!selectedIndustry || !companyName) return;
    setCreating(true);
    setError("");
    try {
      await api.createCompany({
        name: companyName,
        industry: selectedIndustry,
        growth_stage: growthStage,
        culture_type: cultureType,
        num_people: numPeople,
      });
      navigate("/");
    } catch (e) {
      setError(String(e));
    }
    setCreating(false);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">
          {t("setup.title")}
        </h1>
        <p className="text-sm text-zinc-500">{t("setup.subtitle")}</p>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center gap-2">
        {[0, 1, 2].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                step === s
                  ? "bg-emerald-500 text-white"
                  : step > s
                    ? "bg-emerald-500/30 text-emerald-400"
                    : "bg-zinc-800 text-zinc-500"
              }`}
            >
              {s + 1}
            </div>
            {s < 2 && (
              <ChevronRight size={14} className="text-zinc-600" />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Industry Selection */}
      {step === 0 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <h2 className="text-lg font-semibold text-zinc-200">
            {t("setup.selectIndustry")}
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {templates.map((tmpl) => {
              const Icon = industryIcons[tmpl.industry] || Building2;
              return (
                <button
                  key={tmpl.industry}
                  onClick={() => setSelectedIndustry(tmpl.industry)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    selectedIndustry === tmpl.industry
                      ? "border-emerald-500 bg-emerald-500/10"
                      : "border-zinc-800 bg-zinc-900 hover:border-zinc-700"
                  }`}
                >
                  <Icon
                    size={24}
                    className={
                      selectedIndustry === tmpl.industry
                        ? "text-emerald-400"
                        : "text-zinc-500"
                    }
                  />
                  <p className="mt-2 text-sm font-medium text-zinc-200">
                    {lang === "ko" ? tmpl.name_ko : tmpl.name_en}
                  </p>
                  <p className="text-xs text-zinc-500 mt-1">
                    {tmpl.departments.length} {t("setup.departments")} · {tmpl.roles.length}{" "}
                    {t("setup.roles")}
                  </p>
                </button>
              );
            })}
          </div>
          <button
            onClick={() => setStep(1)}
            disabled={!selectedIndustry}
            className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-30 transition-colors"
          >
            {t("common.confirm")} →
          </button>
        </motion.div>
      )}

      {/* Step 2: Company Settings */}
      {step === 1 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <h2 className="text-lg font-semibold text-zinc-200">
            {t("setup.companySettings")}
          </h2>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-zinc-500 block mb-1">
                {t("setup.companyName")}
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="TechVenture Inc."
                className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="text-xs text-zinc-500 block mb-1">
                {t("setup.teamSize")} ({numPeople})
              </label>
              <input
                type="range"
                min={5}
                max={50}
                value={numPeople}
                onChange={(e) => setNumPeople(parseInt(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs text-zinc-500 block mb-1">
                {t("setup.growthStage")}
              </label>
              <div className="flex gap-2">
                {growthStages.map((gs) => (
                  <button
                    key={gs}
                    onClick={() => setGrowthStage(gs)}
                    className={`px-3 py-1.5 rounded-lg text-xs ${
                      growthStage === gs
                        ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                    }`}
                  >
                    {t(`setup.stages.${gs}`)}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-zinc-500 block mb-1">
                {t("setup.culture")}
              </label>
              <div className="grid grid-cols-2 gap-2">
                {cultureTypes.map((ct) => (
                  <button
                    key={ct}
                    onClick={() => setCultureType(ct)}
                    className={`px-3 py-2 rounded-lg text-xs text-left ${
                      cultureType === ct
                        ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                    }`}
                  >
                    {t(`setup.cultures.${ct}`)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setStep(0)}
              className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm"
            >
              ← {t("common.cancel")}
            </button>
            <button
              onClick={() => setStep(2)}
              disabled={!companyName}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-30 transition-colors"
            >
              {t("common.confirm")} →
            </button>
          </div>
        </motion.div>
      )}

      {/* Step 3: Preview & Create */}
      {step === 2 && selectedTemplate && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <h2 className="text-lg font-semibold text-zinc-200">
            {t("setup.preview")}
          </h2>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-zinc-500">{t("setup.companyName")}:</span>
                <span className="ml-2 text-zinc-200">{companyName}</span>
              </div>
              <div>
                <span className="text-zinc-500">{t("setup.selectIndustry")}:</span>
                <span className="ml-2 text-zinc-200">
                  {lang === "ko" ? selectedTemplate.name_ko : selectedTemplate.name_en}
                </span>
              </div>
              <div>
                <span className="text-zinc-500">{t("setup.teamSize")}:</span>
                <span className="ml-2 text-zinc-200">{numPeople}</span>
              </div>
              <div>
                <span className="text-zinc-500">{t("setup.growthStage")}:</span>
                <span className="ml-2 text-zinc-200">
                  {t(`setup.stages.${growthStage}`)}
                </span>
              </div>
            </div>

            <div>
              <p className="text-xs text-zinc-500 mb-1">{t("setup.departments")}:</p>
              <div className="flex flex-wrap gap-1">
                {selectedTemplate.departments.map((d) => (
                  <span
                    key={d}
                    className="px-2 py-0.5 rounded bg-zinc-800 text-xs text-zinc-400"
                  >
                    {d}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="text-xs text-zinc-500 mb-1">{t("setup.roles")}:</p>
              <div className="flex flex-wrap gap-1">
                {selectedTemplate.roles.map((r) => (
                  <span
                    key={r}
                    className="px-2 py-0.5 rounded bg-zinc-800 text-xs text-zinc-400"
                  >
                    {r}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-400">{error}</p>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm"
            >
              ← {t("common.cancel")}
            </button>
            <button
              onClick={handleCreate}
              disabled={creating}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-50 transition-colors"
            >
              {creating ? t("common.loading") : t("setup.create")}
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
